import datetime
from functools import wraps
import logging
import os
import sys
import uuid

from flask import (
        flash, 
        redirect, 
        render_template, 
        request, 
        Response,
        session, 
        url_for, 
)
import pytz
from werkzeug.utils import secure_filename

from app import app, db
from forms import (
        OTRSubmissionAdminForm, 
        OTRSubmissionForm, 
        QuoteAdminForm,
        QuoteSubmissionForm
)
from models import User, Picture, Submission, Quote
import tasks


## Authorization
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if app.config['TESTING'] == True and username == 'admin' and password == 'tunch':
        return True
    u = User.query.filter_by(username=username).first()
    if u and u.verify_password(password):
        session['current_user'] = {'username': u.username, 'id': u.id}
        return True
    else:
        session['current_user'] = None
        return False

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
            'Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    '''
    Remember that this goes AFTER @app.route!
    '''
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def not_authorized():
    flash("You aren't authorized to view that post.")
    return redirect(url_for('index'))

def ip_throttled(submission_type, addr, max_submissions=app.config['MAX_SUBMISSIONS_PER_HOUR']):
    one_hour_ago = datetime.datetime.now(pytz.timezone('US/Eastern')) - datetime.timedelta(hours=1)
    recent_by_ip = submission_type.query.filter(
            submission_type.ip_address == addr,
            submission_type.datetime_submitted >= one_hour_ago
    ).all()
    if len(recent_by_ip) > max_submissions:
        return True
    return False

## View functions
@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('submit_on_the_road'))


## On The Road
@app.route('/on-the-road/submit', methods=['GET', 'POST'])
def submit_on_the_road():
    try:
        form = OTRSubmissionForm()
        pictures_to_parse = [p for p in form.pictures if p.upload.data]
    except:
        flash("Something went wrong. Make sure that all of your pictures "
                "are smaller than %sMB." % app.config['MAX_CONTENT_MB']
        )
        return redirect(url_for('submit_on_the_road'))
    slice_index = len(pictures_to_parse) if pictures_to_parse else 1
    if request.method == 'POST' and not pictures_to_parse:
        flash("You need to submit some pictures!")
        return render_template('submit_on_the_road.html', 
                form=form, config=app.config, slice_index=slice_index)        
    if form.validate_on_submit():
        if not app.config['LOCAL']:
            if ip_throttled(Submission, request.remote_addr):
                flash("Your IP address has been used to submit several posts recently. "
                        "Please try again in an hour or so."
                )
                return redirect(url_for('submit_on_the_road'))
        submission = Submission(
                nym=form.nym.data,
                email=form.email.data,
                introduction=form.introduction.data,
                status='pending',
                datetime_submitted=datetime.datetime.now(pytz.timezone('US/Eastern')),
                ip_address=request.remote_addr
        )
        submission_prefix = str(uuid.uuid1())
        for i, picture_form in enumerate(pictures_to_parse):
            if not picture_form.validate(request):
                for error in picture_form.errors: print error
                return render_template('submit_on_the_road.html', 
                        form=form, config=app.config, slice_index=slice_index)
            picture_file = picture_form.upload.data
            extension = secure_filename(picture_form.upload.data.filename).split('.')[-1]
            extension = '.' + extension if extension else ''
            file_name = submission_prefix + str(i) + extension
            file_path = os.path.join(
                    app.config['APPLICATION_WORKING_DIRECTORY'], 
                    'static/submissions',
                    file_name
            )
            try:
                picture_file.save(file_path)
            except:
                flash("Something went wrong uploading picture #%s, %s" % (
                        str(i+1), form.title.data)
                )
                continue
            submission.pictures.append(Picture(
                    title=picture_form.title.data,
                    date_taken=picture_form.date_taken.data,
                    place_taken=picture_form.place_taken.data,
                    picture_description=picture_form.picture_description.data,
                    file_location=file_path
            ))
        db.session.add(submission)
        db.session.commit()
        return redirect(url_for('thanks_on_the_road'))
    if form.errors:
        print form.errors
    return render_template(
            'submit_on_the_road.html', form=form, config=app.config, 
            slice_index=slice_index
    )

@app.route('/on-the-road/thanks/', methods=['GET'])
def thanks_on_the_road():
    return render_template('thanks_on_the_road.html')

@app.route('/on-the-road/admin/', methods=['GET', 'POST'])
@requires_auth
def admin_list_on_the_road():
    form = OTRSubmissionAdminForm()
    if form.validate_on_submit():
        submission = Submission.query.get(form.submission_id.data)
        writer = tasks.BJPostWriter(submission)
        try:
            result = writer.make_draft_post()
        except:
            flash("Something went wrong with the posting. Check to see "
                    "if the pictures have uploaded, and delete them if so..."
            )
            return redirect(url_for('admin_list_on_the_road'))
        flash("Alright, there should be a new draft post up at BJ!")
    pending_submissions = (Submission.query.filter_by(status='pending')
            .order_by(Submission.datetime_submitted.desc()).all()
    )
    return render_template(
            'admin_list_on_the_road.html', form=form,
            pending_submissions=pending_submissions)

@app.route('/on-the-road/admin/submitted/', methods=['GET', 'POST'])
@requires_auth
def admin_list_submitted_on_the_road():
    submissions = (Submission.query.filter_by(status='submitted')
            .order_by(Submission.datetime_submitted.desc()).all()
    )
    return render_template('admin_list_submitted_on_the_road.html', submissions=submissions)

@app.route('/on-the-road/admin/delete/', methods=['POST'])
@requires_auth
def admin_delete_on_the_road():
    form = OTRSubmissionAdminForm()
    if form.validate_on_submit():
        submission = Submission.query.get(form.submission_id.data)
        errs = ""
        for picture in submission.pictures:
            try:
                os.remove(picture.file_location)
            except:
                errs += str(sys.exc_info()[0])
                errs += "....."
        db.session.delete(submission)
        db.session.commit()
        flash("OK, that's been deleted.")
        if errs != "":
            flash("With the following errors: %s" % errs)
    else:
        flash("Something went wrong deleting that submission.")
    return redirect(url_for('admin_list_on_the_road'))


## Quote submission
@app.route('/quotes', methods=['GET'])
def quotes():
    return redirect(url_for('submit_quote'))

@app.route('/quotes/submit/', methods=['GET', 'POST'])
def submit_quote():
    form = QuoteSubmissionForm()
    if form.validate_on_submit():
        if not app.config['LOCAL']:
            if ip_throttled(Quote, request.remote_addr, max_submissions=10):
                flash("Your IP address has been used to submit several posts recently. "
                        "Please try again in an hour or so."
                )
                return redirect(url_for('submit_quote'))
        new_quote = Quote(
                nym=form.nym.data,
                email=form.email.data,
                quote=form.quote.data,
                quote_type=form.quote_type.data,
                datetime_submitted=datetime.datetime.now(pytz.timezone('US/Eastern')),
                ip_address=request.remote_addr
        )
        logging.info("added new quote '%s' from %s" % (
                form.quote.data, form.nym.data
        ))
        db.session.add(new_quote)
        db.session.commit()
        flash("Thanks for your submission!")
        return redirect(url_for('submit_quote'))
    return render_template('submit_quote.html', form=form, config=app.config)


@app.route('/quotes/admin/', methods=['GET'])
@requires_auth
def admin_list_quote():
    form = QuoteAdminForm()
    all_quotes = Quote.query.order_by(Quote.datetime_submitted.desc()).all()
    return render_template(
            'admin_list_quote.html', form=form, all_quotes=all_quotes
    )


@app.route('/quotes/admin/delete/', methods=['POST'])
@requires_auth
def admin_delete_quote():
    form = QuoteAdminForm()
    if form.validate_on_submit():
        quote = Quote.query.get(form.quote_id.data)
        db.session.delete(quote)
        db.session.commit()
        flash("OK, that's been deleted.")
    return redirect(url_for('admin_list_quote'))
