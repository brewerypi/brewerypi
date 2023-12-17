from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length, NumberRange
from .. models import LookupValue

class LookupValueForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired(), Length(1, 45)])
	selectable = BooleanField("Selectable", validators = [NumberRange(min = 0)])
	lookupValueId = HiddenField()
	lookupId = HiddenField()
	value = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		lookupValue = LookupValue.query.filter_by(LookupId = self.lookupId.data, Name = field.data).first()
		if lookupValue:
			if self.lookupValueId.data == "":
				# Trying to add a new lookupValue using a name that already exists.
				validationError = True
			else:
				if int(self.lookupValueId.data) != lookupValue.LookupValueId:
					# Trying to change the name of a lookupValue to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
