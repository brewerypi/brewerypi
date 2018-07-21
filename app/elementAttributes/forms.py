from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import HiddenField, SelectField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required
from .. models import Area, Element, Enterprise, Site, Tag
from .. helpers import tagFullyAbbreviatedPath

class ElementAttributeForm(FlaskForm):
	elementAttributeTemplate = QuerySelectField("Element Attribute Template", validators = [Required()],
		get_label = "Name")
	tag = QuerySelectField(query_factory = lambda: Tag.query.join(Area, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name), get_label = tagFullyAbbreviatedPath)
	elementId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

class ElementAttributeImportForm(FlaskForm):
	elementAttributesFile = FileField("Element Attributes Import File", validators = [FileRequired(), FileAllowed(["csv"], ".csv files only!")])
	submit = SubmitField("Import")
