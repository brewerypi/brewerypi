from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required
from .. helpers import elementTemplateFullyAbbreviatedPath
from .. models import Element, ElementTemplate, Enterprise, Site

class ElementForm(FlaskForm):
	elementTemplate = QuerySelectField("Element Template", query_factory = lambda: ElementTemplate.query.join(Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name), get_label = elementTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	submit = SubmitField("Save")
