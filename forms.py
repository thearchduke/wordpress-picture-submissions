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
    place_taken = fields.TextAreaField(
            'Where was this taken? (optional)',
            validators=[Optional()]
    )


class BJSubmissionForm(FlaskForm):
    nym = fields.StringField('Screenname', validators=[DataRequired()])
    email = fields.StringField(
            'Email (private, for verification and feedback)',
            validators=[DataRequired()])

    if not config.LOCAL:
        recaptcha = RecaptchaField()

    verification_error = ("Something went wrong verifying this "
            "email and username combination. If you haven't "
            "commented at Balloon-Juice before, go comment in an "
            "active thread, wait for it to get approved, and come "
            "submit again."
    )

    def validate(form):
        if not Form.validate(form):
            return False
        result = True
        wp = wordpress.WordpressAPI()
        if not wp.verify_nym(form.nym.data, form.email.data):
            form.email.errors.append(form.verification_error)
            result = False
        return result


class OTRSubmissionForm(BJSubmissionForm):
    introduction = fields.TextAreaField(
            'General introduction/description', validators=[DataRequired()]
    )
    pictures = fields.FieldList(
            fields.FormField(PictureForm), 
            min_entries=config.MAX_PICTURES, 
            max_entries=config.MAX_PICTURES,
            validators=[Optional()]
    )

    verification_error = ("Something went wrong verifying this "
            "email and username combination. If you haven't "
            "commented at Balloon-Juice before, go comment in an "
            "active thread, wait for it to get approved, and come "
            "submit your pictures again. Alternatively, email your "
            "pictures to please@getmechamot.com"
    )


class OTRSubmissionAdminForm(FlaskForm):
    submission_id = fields.HiddenField()


class QuoteSubmissionForm(BJSubmissionForm):
    quote = fields.TextAreaField('Quote', validators=[DataRequired()])
    quote_type = fields.SelectField(
            'Quote type', 
            choices=[('pie', 'Pie Filter'), ('rotating', 'Rotating')],
            validators=[DataRequired()]
    )

    verification_error = ("Something went wrong verifying this "
            "email and username combination. If you haven't "
            "commented at Balloon-Juice before, just go ahead and "
            "leave your quote suggestion in a comment."
    )


class QuoteAdminForm(FlaskForm):
    quote_id = fields.HiddenField()
