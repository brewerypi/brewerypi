from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError 
from wtforms.validators import Length, Required
from .. models import UnitOfMeasurement

class UnitOfMeasurementForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators = [Required(), Length(1, 15)])
	unitOfMeasurementId = HiddenField()
	submit = SubmitField("Save")

	def validate_abbreviation(self, field):
		validationError = False
		unitOfMeasurement = UnitOfMeasurement.query.filter_by(Abbreviation = field.data, Name = self.name.data).first()
		if unitOfMeasurement:
			if self.unitOfMeasurementId.data == "":
				# Trying to add a new unitOfMeasurement using an abbreviation and name that already exists.
				validationError = True
			else:
				if int(self.unitOfMeasurementId.data) != unitOfMeasurement.UnitOfMeasurementId:
					# Trying to change the name of an unitOfMeasurement to an abbreviation and name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The abbreviation "{}" and name "{}" already exists.'.format(field.data, self.name.data))

	def validate_name(self, field):
		validationError = False
		unitOfMeasurement = UnitOfMeasurement.query.filter_by(Abbreviation = self.abbreviation.data, Name = field.data).first()
		if unitOfMeasurement:
			if self.unitOfMeasurementId.data == "":
				# Trying to add a new unitOfMeasurement using an abbreviation and name that already exists.
				validationError = True
			else:
				if int(self.unitOfMeasurementId.data) != unitOfMeasurement.UnitOfMeasurementId:
					# Trying to change the name of an unitOfMeasurement to an abbreviation and name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The abbreviation "{}" and name "{}" already exists.'.format(self.abbreviation.data, field.data))
