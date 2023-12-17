from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length
from .. models import Enterprise

class EnterpriseForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators = [DataRequired(), Length(1, 10)])
	description = StringField("Description", validators = [Length(0, 255)])
	enterpriseId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_abbreviation(self, field):
		validationError = False
		enterprise = Enterprise.query.filter_by(Abbreviation = field.data).first()
		if enterprise:
			if self.enterpriseId.data == "":
				# Trying to add a new enterprise using an abbreviation that already exists.
				validationError = True
			else:
				if int(self.enterpriseId.data) != enterprise.EnterpriseId:
					# Trying to change the abbreviation of an enterprise to an abbreviation that already exists.
					validationError = True

		if validationError:
			raise ValidationError('The abbreviation "{}" already exists.'.format(field.data))

	def validate_name(self, field):
		validationError = False
		enterprise = Enterprise.query.filter_by(Name = field.data).first()
		if enterprise:
			if self.enterpriseId.data == "":
				# Trying to add a new enterprise using a name that already exists.
				validationError = True
			else:
				if int(self.enterpriseId.data) != enterprise.EnterpriseId:
					# Trying to change the name of an enterprise to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
