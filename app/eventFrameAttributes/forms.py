from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField

class EventFrameAttributeImportForm(FlaskForm):
	eventFrameAttributesFile = FileField("Event Frame Attributes Import File", validators = [FileRequired(), FileAllowed(["csv"], ".csv files only!")])
	submit = SubmitField("Import")
