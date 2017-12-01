# app/admin/forms.py

from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, FloatField, StringField, SubmitField, TextField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required

from .. models import Area, AttributeTemplate, Element, ElementTemplate, Enterprise, Lookup, Site, Tag, UnitOfMeasurement

def areaFullyAbbreviatedPath(area):
	return area.Site.Enterprise.Abbreviation + "_" + area.Site.Abbreviation + "_" + area.Abbreviation

def attributeTemplateFullyAbbreviatedPath(attributeTemplate):
	return attributeTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + attributeTemplate.ElementTemplate.Site.Abbreviation + "_" + attributeTemplate.ElementTemplate.Name + "_" + attributeTemplate.Name

def elementFullyAbbreviatedPath(element):
	return element.ElementTemplate.Site.Enterprise.Abbreviation + "_" + element.ElementTemplate.Site.Abbreviation + "_" + element.ElementTemplate.Name + "_" + element.Name

def elementTemplateFullyAbbreviatedPath(elementTemplate):
	return elementTemplate.Site.Enterprise.Abbreviation + "_" + elementTemplate.Site.Abbreviation + "_" + elementTemplate.Name

def lookupFullyAbbreviatedPath(lookup):
	return lookup.Enterprise.Abbreviation + "_" + lookup.Name

def siteFullyAbbreviatedPath(site):
	return site.Enterprise.Abbreviation + "_" + site.Abbreviation

def tagFullyAbbreviatedPath(tag):
	return tag.Area.Site.Enterprise.Abbreviation + "_" + tag.Area.Site.Abbreviation + "_" + tag.Area.Abbreviation + "_" + tag.Name

class AreaForm(FlaskForm):
	site = QuerySelectField(query_factory=lambda: Site.query.join(Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation), get_label=siteFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators=[Required(), Length(1, 10)])
	description = TextField("Description", validators=[Length(0, 255)])
	submit = SubmitField('Save')

class AttributeTemplateForm(FlaskForm):
	elementTemplate = QuerySelectField(query_factory=lambda: ElementTemplate.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name), get_label=elementTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	description = TextField("Description", validators=[Length(0, 255)])
	submit = SubmitField('Save')

class ElementAttributeForm(FlaskForm):
	element = QuerySelectField(query_factory=lambda: Element.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name), get_label=elementFullyAbbreviatedPath)
	attributeTemplate = QuerySelectField(query_factory=lambda: AttributeTemplate.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, AttributeTemplate.Name), get_label=attributeTemplateFullyAbbreviatedPath)
	tag = QuerySelectField(query_factory=lambda: Tag.query.join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name), get_label=tagFullyAbbreviatedPath)
	submit = SubmitField('Save')

class ElementForm(FlaskForm):
	elementTemplate = QuerySelectField(query_factory=lambda: ElementTemplate.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name), get_label=elementTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	description = TextField("Description", validators=[Length(0, 255)])
	submit = SubmitField('Save')

class ElementTemplateForm(FlaskForm):
	site = QuerySelectField(query_factory=lambda: Site.query.join(Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation), get_label=siteFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	description = TextField("Description", validators=[Length(0, 255)])
	submit = SubmitField('Save')

class EnterpriseForm(FlaskForm):
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators=[Required(), Length(1, 10)])
	description = TextField("Description", validators=[Length(0, 255)])
	submit = SubmitField('Save')

class LookupForm(FlaskForm):
	enterprise = QuerySelectField(query_factory=lambda: Enterprise.query.order_by(Enterprise.Abbreviation), get_label="Abbreviation")
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	submit = SubmitField('Save')

class LookupValueForm(FlaskForm):
	lookup = QuerySelectField(query_factory=lambda: Lookup.query.join(Enterprise).order_by(Enterprise.Abbreviation, Lookup.Name), get_label=lookupFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	submit = SubmitField('Save')

class SiteForm(FlaskForm):
	enterprise = QuerySelectField(query_factory=lambda: Enterprise.query.order_by(Enterprise.Abbreviation), get_label="Abbreviation")
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators=[Required(), Length(1, 10)])
	description = TextField("Description", validators=[Length(0, 255)])
	submit = SubmitField('Save')

class TagForm(FlaskForm):
	area = QuerySelectField(query_factory=lambda: Area.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation), get_label=areaFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	description = TextField("Description", validators=[Length(0, 255)])
	unitOfMeasurement = QuerySelectField("Unit", query_factory=lambda: UnitOfMeasurement.query.order_by(UnitOfMeasurement.Abbreviation), get_label="Abbreviation")
	submit = SubmitField('Save')

class TagValueForm(FlaskForm):
	tag = QuerySelectField(query_factory=lambda: Tag.query.join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name), get_label=tagFullyAbbreviatedPath)
	timestamp = DateTimeField("Timestamp", default=datetime.now, validators=[Required()])
	value = FloatField("Value", validators=[Required()])
	submit = SubmitField('Save')

class UnitOfMeasurementForm(FlaskForm):
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators=[Required(), Length(1, 15)])
	submit = SubmitField('Save')
