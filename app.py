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

from forms import imagefiles


app = Flask('on_the_road')
app.config.from_object('config')
db = SQLAlchemy(app)
configure_uploads(app, (imagefiles,))
import views


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


@app.route('/', methods=['GET'])
def index():
    return redirect(url_for('submit'))

@app.route('/thanks/', methods=['GET'])
def thanks():
    return views.thanks()

@app.route('/submit/', methods=['GET', 'POST'])
def submit():
    return views.submit()

@app.route('/admin/', methods=['GET'])
def admin_list():
    return views.admin_list()

@app.route('/admin/<submission_id>', methods=['GET'])
def admin_detail(submission_id):
    return views.admin_detail(submission_id)

if __name__ == '__main__':
    db.create_all()
    app.run(host='0.0.0.0', port=5001, debug=app.config['TESTING'])
