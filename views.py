import datetime
from functools import wraps
import os
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
from werkzeug.utils import secure_filename

from app import app, db, User, Picture, Submission
from forms import BJSubmissionForm


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
    return redirect(url_for('.home'))


## View functions
def submit():
    print "um"
    try:
        form = BJSubmissionForm()
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
        submission = Submission(
                nym=form.nym.data,
                email=form.email.data,
                introduction=form.introduction.data,
                status='pending',
                datetime_submitted=datetime.datetime.now(),
                ip_address=str(request.remote_addr)
        )
        submission_prefix = str(uuid.uuid1())
        for i, picture_form in enumerate(pictures_to_parse):
            if not picture_form.validate(request):
                return render_template('submit.html', 
                        form=form, config=app.config, slice_index=slice_index)
            picture_file = picture_form.upload.data
            extension = secure_filename(picture_form.upload.data.filename).split('.')[-1]
            extension = '.' + extension if extension else ''
            file_name = submission_prefix + str(i) + extension
            file_path = os.path.join(
                    app.config['APPLICATION_WORKING_DIRECTORY'], 
                    'submissions',
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

def thanks():
    return render_template('thanks.html')

@requires_auth
def admin_list():
    pending_submissions = Submission.query.filter_by(status='pending').all()
    return render_template('admin_list.html', pending_submissions=pending_submissions)
    return "admin page!"

@requires_auth
def admin_detail(submission_id):
    submission = Submission.query.get_or_404(submission_id)
    return render_template('admin_detail.html', submission=submission)