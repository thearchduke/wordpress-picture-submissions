import socket 

from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import fields, Form
from wtforms.validators import DataRequired, Optional


imagefiles = UploadSet('images', IMAGES)


class PictureForm(Form):
    upload = FileField('Picture', validators=[
            FileRequired(), 
            FileAllowed(imagefiles, 'Images only')
    ])
    title = fields.StringField('Title (optional)')
    picture_description = fields.TextAreaField(
            'Picture description (shows before picture)',
            validators=[DataRequired()]
    )
    date_taken = fields.DateField(
            'Date picture taken (optional)',
            format='%m/%d/%Y',
            validators=[Optional()]
    )


class BJSubmissionForm(FlaskForm):
    nym = fields.StringField('Screenname', validators=[DataRequired()])
    email = fields.StringField(
            'Email (private, for verification and feedback)',
            validators=[DataRequired()])
    introduction = fields.TextAreaField(
            'General introduction/description', validators=[DataRequired()]
    )
    pictures = fields.FieldList(fields.FormField(PictureForm), min_entries=1)

    if socket.gethostname() == 'test.balloon-juice.com':
        recaptcha = RecaptchaField()
