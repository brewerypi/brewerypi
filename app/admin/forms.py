from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, FloatField, IntegerField, SelectField, StringField, SubmitField, TextField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required, Optional
from app import db
import sqlalchemy

from .. models import Area, AttributeTemplate, Element, ElementTemplate, EventFrame, EventFrameTemplate, Enterprise, Site, Tag, UnitOfMeasurement

def areaFullyAbbreviatedPath(area):
	return area.Site.Enterprise.Abbreviation + "_" + area.Site.Abbreviation + "_" + area.Abbreviation

def attributeTemplateFullyAbbreviatedPath(attributeTemplate):
	return attributeTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + attributeTemplate.ElementTemplate.Site.Abbreviation + "_" + \
		attributeTemplate.ElementTemplate.Name + "_" + attributeTemplate.Name

def elementFullyAbbreviatedPath(element):
	return element.ElementTemplate.Site.Enterprise.Abbreviation + "_" + element.ElementTemplate.Site.Abbreviation + "_" + element.ElementTemplate.Name + "_" \
		+ element.Name

def elementTemplateFullyAbbreviatedPath(elementTemplate):
	return elementTemplate.Site.Enterprise.Abbreviation + "_" + elementTemplate.Site.Abbreviation + "_" + elementTemplate.Name

def eventFrameFullyAbbreviatedPath(eventFrame):
	return eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + eventFrame.EventFrameTemplate.ElementTemplate.Site.Abbreviation \
		+ "_" + eventFrame.EventFrameTemplate.ElementTemplate.Name + "_" + eventFrame.EventFrameTemplate.Name + "_" + eventFrame.Name

def eventFrameTemplateFullyAbbreviatedPath(eventFrameTemplate):
	return eventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + eventFrameTemplate.ElementTemplate.Site.Abbreviation + "_" + \
			eventFrameTemplate.ElementTemplate.Name + "_" + eventFrameTemplate.Name

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

class EventFrameForm(FlaskForm):
	eventFrameTemplate = QuerySelectField("Event Frame Template", query_factory=lambda: EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise)\
		.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name), get_label=eventFrameTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	description = TextField("Description", validators=[Length(0, 255)])
	parentEventFrame = QuerySelectField("Parent Event Frame", query_factory=lambda: EventFrame.query.join(EventFrameTemplate, ElementTemplate, Site, \
		Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name, EventFrame.Name), \
		get_label=eventFrameFullyAbbreviatedPath, allow_blank=True)
	order = IntegerField("Order", validators=[Required()])
	startTime = DateTimeField("Start Time", default=datetime.now, validators=[Required()])
	endTime = DateTimeField("End Time", validators=[Optional()])
	submit = SubmitField('Save')

class EventFrameTemplateForm(FlaskForm):
	elementTemplate = QuerySelectField("Element Template", query_factory=lambda: ElementTemplate.query.join(Site, Enterprise)\
		.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name), get_label=elementTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	description = TextField("Description", validators=[Length(0, 255)])
	parentEventFrameTemplate = QuerySelectField("Parent Event Frame Template", query_factory=lambda: EventFrameTemplate.query.join(ElementTemplate, Site, \
		Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name), \
		get_label=eventFrameTemplateFullyAbbreviatedPath, allow_blank=True)
	submit = SubmitField('Save')

class SiteForm(FlaskForm):
	enterprise = QuerySelectField(query_factory=lambda: Enterprise.query.order_by(Enterprise.Abbreviation), get_label="Abbreviation")
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators=[Required(), Length(1, 10)])
	description = TextField("Description", validators=[Length(0, 255)])
	submit = SubmitField('Save')

class UnitOfMeasurementForm(FlaskForm):
	name = StringField("Name", validators=[Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators=[Required(), Length(1, 15)])
	submit = SubmitField('Save')
