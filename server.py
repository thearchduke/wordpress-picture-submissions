#!/usr/bin/env python
import datetime
from functools import wraps
import os
import sys
import uuid

from flask import (
        flash, 
        Flask, 
        redirect, 
        render_template, 
        request, 
        Response,
        session, 
        url_for, 
)
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename

from forms import BJSubmissionForm, imagefiles


app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
configure_uploads(app, (imagefiles,))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    hashed_password = db.Column(db.String(256))

    def hash_password(self, password):
        hashed_password = sha256_crypt.encrypt(password)
        return hashed_password

    def verify_password(self, challenge):
        test = sha256_crypt.verify(challenge, self.hashed_password)
        return test

    def __init__(self, username, password):
        self.username = username
        self.hashed_password = self.hash_password(password)

    def __repr__(self):
        return '<User %r>' % self.username


class Submission(db.Model):
    # sql
    id = db.Column(db.Integer, primary_key=True)
    # submitted
    nym = db.Column(db.String(1024))
    email = db.Column(db.String(1024))
    introduction = db.Column(db.Text())
    pictures = db.relationship(
            'Picture', backref='submission', lazy='dynamic'
    )
    # metadata
    status = db.Column(db.String(64))
    successfully_posted = db.Column(db.Boolean())
    datetime_submitted = db.Column(db.DateTime())
    datetime_approved = db.Column(db.DateTime())
    datetime_posted = db.Column(db.DateTime())
    ip_address = db.Column(db.String(256))
    # date/time
    # ip
    # etc.


class Picture(db.Model):
    # sql
    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey('submission.id'))
    # submitted
    title = db.Column(db.Text())
    date_taken = db.Column(db.Date())
    picture_description = db.Column(db.Text())
    # meta
    file_location = db.Column(db.String(1024))


## Authorization
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    u = db.session.query(User).filter(User.username == username).first()
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


@app.route('/', methods=['GET'])
def hello_world():
    return redirect(url_for('submit'))

@app.route('/thanks', methods=['GET'])
def thanks():
    return "thanks!"

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    form = BJSubmissionForm()
    pictures_to_parse = [p for p in form.pictures if p.upload.data]
    slice_index = len(pictures_to_parse) if pictures_to_parse else 1
    if request.method == 'POST' and not pictures_to_parse:
        flash("You need to submit some pictures!")
        return render_template('submit.html', 
                form=form, local=app.config['LOCAL'], slice_index=slice_index)        
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
                        form=form, local=app.config['LOCAL'], slice_index=slice_index)
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
        flash("Thanks for your submission!")
        return redirect(url_for('thanks'))
    if form.errors:
        print form.errors
    return render_template(
            'submit.html', form=form, local=app.config['LOCAL'], 
            slice_index=slice_index
    )

@app.route('/admin', methods=['GET'])
@requires_auth
def admin():
    pass

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
