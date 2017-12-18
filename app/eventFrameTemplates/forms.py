from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required, ValidationError
from .. helpers import elementTemplateFullyAbbreviatedPath, eventFrameTemplateFullyAbbreviatedPath
from .. models import ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Site

class EventFrameTemplateForm(FlaskForm):
	elementTemplate = QuerySelectField("Element Template", query_factory = lambda: ElementTemplate.query.join(Site, Enterprise)\
		.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name), get_label = elementTemplateFullyAbbreviatedPath)
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	parentEventFrameTemplate = QuerySelectField("Parent Event Frame Template", query_factory = lambda: EventFrameTemplate.query.join(ElementTemplate, Site, \
		Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name), \
		get_label = eventFrameTemplateFullyAbbreviatedPath, allow_blank = True)
	submit = SubmitField("Save")

	def validate_parentEventFrameTemplate(form, field):
		if field.data != None:
			if field.data.ElementTemplateId != form.elementTemplate.data.ElementTemplateId:
				raise ValidationError("Parent Event Frame must be blank or of the same element template type.")
