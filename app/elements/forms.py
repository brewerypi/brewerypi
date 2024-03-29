from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SelectField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from .. models import Element

class ElementForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	isManaged = BooleanField("Manage Tags", default = "checked")
	area = SelectField("Area", validators = [DataRequired()], coerce = int)
	elementId = HiddenField()
	elementIdToCopy = HiddenField()
	elementTemplateId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		element = Element.query.filter_by(ElementTemplateId = self.elementTemplateId.data, Name = field.data).first()
		if element:
			if self.elementId.data == "":
				# Trying to add a new element using a name that already exists.
				validationError = True
			else:
				if int(self.elementId.data) != element.ElementId:
					# Trying to change the name of an element to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
