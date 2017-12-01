from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import DateTimeField, FloatField, SubmitField, TextField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required

from .. models import Element, ElementTemplate, Enterprise, Site

def elementFullyAbbreviatedPath(element):

	return element.ElementTemplate.Site.Enterprise.Abbreviation + "_" + element.ElementTemplate.Site.Abbreviation + "_" + element.ElementTemplate.Name + "_" + element.Name

class ElementForm(FlaskForm):

	element = QuerySelectField("Element", query_factory=lambda: Element.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name), get_label=elementFullyAbbreviatedPath)
	submit = SubmitField('Select')

class ElementAttributeValueForm(FlaskForm):

	timestamp = DateTimeField("Timestamp", default=datetime.now, validators=[Required()])
	value = FloatField("Value", validators=[Required()])
	submit = SubmitField('Save')
