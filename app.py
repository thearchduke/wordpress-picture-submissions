#!/usr/bin/env python
import datetime
from functools import wraps
import os
import sys
import uuid

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import configure_uploads
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename

from forms import imagefiles


app = Flask('on_the_road')
app.config.from_object('config')
db = SQLAlchemy(app)
configure_uploads(app, (imagefiles,))
#import views
