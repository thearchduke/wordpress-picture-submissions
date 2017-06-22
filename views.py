import datetime
from functools import wraps
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
from forms import SubmissionAdminForm, SubmissionForm
from models import User, Picture, Submission
import tasks


## Authorization
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    if app.config['TESTING'] == True and username == 'admin' and password == 'admin':
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

def ip_throttled(addr):
    one_hour_ago = datetime.datetime.now(pytz.timezone('US/Eastern')) - datetime.timedelta(hours=1)
    recent_by_ip = Submission.query.filter(
            Submission.ip_address == ip_address,
            Submission.datetime_submitted >= one_hour_ago
    ).all()
    if len(recent_by_ip) > app.config['MAX_SUBMISSIONS_PER_HOUR']:
        return True
    return False

## View functions
@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('submit'))

@app.route('/submit/', methods=['GET', 'POST'])
def submit():
    try:
        form = SubmissionForm()
        pictures_to_parse = [p for p in form.pictures if p.upload.data]
    except:
        flash("Something went wrong. Make sure that all of your pictures "
                "are smaller than %sMB." % app.config['MAX_CONTENT_MB']
        )
        return redirect(url_for('submit'))
    slice_index = len(pictures_to_parse) if pictures_to_parse else 1
    if request.method == 'POST' and not pictures_to_parse:
        flash("You need to submit some pictures!")
        return render_template('submit.html', 
                form=form, config=app.config, slice_index=slice_index)        
    if form.validate_on_submit():
        if not app.config['LOCAL']:
            if ip_throttled(request.remote_addr):
                flash("Your IP address has been used to submit several posts recently. "
                        "Please try again in an hour or so."
                )
                return redirect(url_for('submit'))
        submission = Submission(
                nym=form.nym.data,
                email=form.email.data,
                introduction=form.introduction.data,
                status='pending',
                datetime_submitted=datetime.datetime.now(pytz.timezone('US/Eastern')),
                ip_address=ip_address
        )
        submission_prefix = str(uuid.uuid1())
        for i, picture_form in enumerate(pictures_to_parse):
            if not picture_form.validate(request):
                for error in picture_form.errors: print error
                return render_template('submit.html', 
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
        return redirect(url_for('thanks'))
    if form.errors:
        print form.errors
    return render_template(
            'submit.html', form=form, config=app.config, 
            slice_index=slice_index
    )

@app.route('/thanks/', methods=['GET'])
def thanks():
    return render_template('thanks.html')

@app.route('/admin/', methods=['GET', 'POST'])
@requires_auth
def admin_list():
    form = SubmissionAdminForm()
    if form.validate_on_submit():
        submission = Submission.query.get(form.submission_id.data)
        writer = tasks.BJPostWriter(submission)
        try:
            result = writer.make_draft_post()
        except:
            flash("Something went wrong with the posting. Check to see "
                    "if the pictures have uploaded, and delete them if so..."
            )
            return redirect(url_for('admin_list'))
        flash("Alright, there should be a new draft post up at BJ!")
    pending_submissions = (Submission.query.filter_by(status='pending')
            .order_by(Submission.datetime_submitted.desc()).all()
    )
    return render_template(
            'admin_list.html', form=form,
            pending_submissions=pending_submissions)

@app.route('/admin/submitted/', methods=['GET', 'POST'])
@requires_auth
def admin_list_submitted():
    submissions = (Submission.query.filter_by(status='submitted')
            .order_by(Submission.datetime_submitted.desc()).all()
    )
    return render_template('admin_list_submitted.html', submissions=submissions)

@app.route('/admin/delete', methods=['POST'])
@requires_auth
def admin_delete():
    form = SubmissionAdminForm()
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
    return redirect(url_for('admin_list'))
