from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import DateTimeField, FloatField, HiddenField, SelectField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required

from .. models import Area, AttributeTemplate, Element, ElementTemplate, Enterprise, Site, Tag
from .. helpers import attributeTemplateFullyAbbreviatedPath, elementFullyAbbreviatedPath, tagFullyAbbreviatedPath

class ElementAttributeForm(FlaskForm):
	element = QuerySelectField(query_factory = lambda: Element.query.join(ElementTemplate, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name), get_label = elementFullyAbbreviatedPath)
	attributeTemplate = QuerySelectField("Attribute Template", query_factory = lambda: AttributeTemplate.query.join(ElementTemplate, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, AttributeTemplate.Name), get_label = attributeTemplateFullyAbbreviatedPath)
	tag = QuerySelectField(query_factory = lambda: Tag.query.join(Area, Site, Enterprise). \
		order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name), get_label = tagFullyAbbreviatedPath)
	submit = SubmitField("Save")

class ElementAttributeValueForm(FlaskForm):
	tagId = HiddenField()
	timestamp = DateTimeField("Timestamp", default = datetime.now, validators = [Required()])
	value = FloatField("Value")
	lookupValue = SelectField("Lookup", coerce = float)
	submit = SubmitField("Save")
