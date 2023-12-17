from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from .. models import Lookup

class LookupForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired(), Length(1, 45)])
	lookupId = HiddenField()
	enterpriseId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		lookup = Lookup.query.filter_by(EnterpriseId = self.enterpriseId.data, Name = field.data).first()
		if lookup:
			if self.lookupId.data == "":
				# Trying to add a new lookup using a name that already exists.
				validationError = True
			else:
				if int(self.lookupId.data) != lookup.LookupId:
					# Trying to change the name of a lookup to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
