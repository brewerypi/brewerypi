from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import SubmitField

class UploadTagsForm(FlaskForm):
	tags = FileField(validators = [FileRequired()])
	submit = SubmitField("Upload")
