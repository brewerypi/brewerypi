from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField

from .. models import Element, ElementTemplate, Enterprise, Site

def elementFullyAbbreviatedPath(element):
	return element.ElementTemplate.Site.Enterprise.Abbreviation + "_" + element.ElementTemplate.Site.Abbreviation + "_" + \
		element.ElementTemplate.Name + "_" + element.Name

class SelectElementForm(FlaskForm):
	element = QuerySelectField("Element", query_factory = lambda: Element.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, \
		Site.Abbreviation, ElementTemplate.Name, Element.Name), get_label = elementFullyAbbreviatedPath)
	submit = SubmitField('Select')
