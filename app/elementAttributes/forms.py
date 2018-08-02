from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField

class ElementAttributeImportForm(FlaskForm):
	elementAttributesFile = FileField("Element Attributes Import File", validators = [FileRequired(), FileAllowed(["csv"], ".csv files only!")])
	submit = SubmitField("Import")
