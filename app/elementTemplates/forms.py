from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from .. models import ElementTemplate

class ElementTemplateForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	elementTemplateId = HiddenField()
	siteId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		elementTemplate = ElementTemplate.query.filter_by(SiteId = self.siteId.data, Name = field.data).first()
		if elementTemplate:
			if self.elementTemplateId.data == "":
				# Trying to add a new elementTemplate using a name that already exists.
				validationError = True
			else:
				if int(self.elementTemplateId.data) != elementTemplate.ElementTemplateId:
					# Trying to change the name of an elementTemplate to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
