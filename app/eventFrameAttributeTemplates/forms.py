from flask_wtf import FlaskForm
from wtforms import HiddenField, FloatField, SelectField, StringField, SubmitField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Optional, Required
from .. models import EventFrameAttributeTemplate, Lookup, LookupValue, UnitOfMeasurement

class EventFrameAttributeTemplateForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	lookup = QuerySelectField("Lookup", query_factory = lambda: Lookup.query.order_by(Lookup.Name), validators = [Required()], get_label = "Name")
	defaultStartLookupValue = SelectField("Default Start Value", validators = [Optional()], coerce = float)
	defaultEndLookupValue = SelectField("Default End Value", validators = [Optional()], coerce = float)
	unitOfMeasurement = QuerySelectField("Unit", query_factory = lambda: UnitOfMeasurement.query. \
		order_by(UnitOfMeasurement.Abbreviation), get_label = "Abbreviation")
	defaultStartValue = FloatField("Default Start Value", validators = [Optional()])
	defaultEndValue = FloatField("Default End Value", validators = [Optional()])
	eventFrameAttributeTemplateId = HiddenField()
	eventFrameTemplateId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		eventFrameAttributeTemplate = EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = self.eventFrameTemplateId.data,
			Name = field.data).first()
		if eventFrameAttributeTemplate:
			if self.eventFrameAttributeTemplateId.data == "":
				# Trying to add a new eventFrameAttributeTemplate using a name that already exists.
				validationError = True
			else:
				if int(self.eventFrameAttributeTemplateId.data) != eventFrameAttributeTemplate.EventFrameAttributeTemplateId:
					# Trying to change the name of an eventFrameAttributeTemplate to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
