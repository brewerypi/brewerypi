from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required

from .. helpers import siteFullyAbbreviatedPath
from .. models import Enterprise, Site

class ElementTemplateForm(FlaskForm):
	site = QuerySelectField(query_factory = lambda: Site.query.join(Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation), get_label = siteFullyAbbreviatedPath)
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	submit = SubmitField("Save")
