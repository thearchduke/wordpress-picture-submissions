from flask_uploads import UploadSet, IMAGES
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import fields, Form
from wtforms.validators import DataRequired

image_set = UploadSet('images', IMAGES)


class PictureForm(Form):
    upload = FileField('Picture', validators=[
            FileRequired(), 
            FileAllowed(image_set, 'Images only')
    ])
    title = fields.StringField('Title (optional)')
    date = fields.DateField('Date picture taken (optional)')
    description = fields.TextAreaField(
            'Picture description (shows before picture)',
            validators=[DataRequired()]
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
    #TODO: recaptcha https://flask-wtf.readthedocs.io/en/stable/form.html
