import config
from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm, RecaptchaField
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import fields, Form
from wtforms.validators import DataRequired, Optional, ValidationError

import wordpress


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
    pictures = fields.FieldList(
            fields.FormField(PictureForm), 
            min_entries=config.MAX_PICTURES, 
            max_entries=config.MAX_PICTURES,
            validators=[Optional()]
    )

    if not config.LOCAL:
        recaptcha = RecaptchaField()

    def validate(form):
        if not Form.validate(form):
            return False
        result = True
        wp = wordpress.WordpressAPI(local=config.LOCAL)
        if not wp.verify_nym(form.nym.data, form.email.data):
            form.email.errors.append("Something went wrong verifying this "
                    "email and username combination. If you haven't "
                    "commented at Balloon-Juice before, go comment in an "
                    "active thread, wait for it to get approved, and come "
                    "submit your pictures again. Alternatively, email your "
                    "pictures to please@getmechamot.com"
            )
            result = False
        return result
