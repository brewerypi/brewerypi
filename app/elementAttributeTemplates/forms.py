from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length 
from wtforms_sqlalchemy.fields import QuerySelectField
from .. models import ElementAttributeTemplate, Lookup, UnitOfMeasurement

class ElementAttributeTemplateForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	lookup = SelectField("Lookup", validators = [DataRequired()], coerce = int)
	unitOfMeasurement = QuerySelectField("Unit", query_factory = lambda: UnitOfMeasurement.query. \
		order_by(UnitOfMeasurement.Abbreviation), get_label = "Abbreviation")
	elementAttributeTemplateId = HiddenField()
	elementTemplateId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		elementAttributeTemplate = ElementAttributeTemplate.query.filter_by(ElementTemplateId = self.elementTemplateId.data, Name = field.data).first()
		if elementAttributeTemplate:
			if self.elementAttributeTemplateId.data == "":
				# Trying to add a new elementAttributeTemplate using a name that already exists.
				validationError = True
			else:
				if int(self.elementAttributeTemplateId.data) != elementAttributeTemplate.ElementAttributeTemplateId:
					# Trying to change the name of an elementAttributeTemplate to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
