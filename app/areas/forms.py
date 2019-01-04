from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import Length, Required
from .. models import Area

class AreaForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators = [Required(), Length(1, 10)])
	description = StringField("Description", validators = [Length(0, 255)])
	areaId = HiddenField()
	siteId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_abbreviation(self, field):
		validationError = False
		area = Area.query.filter_by(Abbreviation = field.data, SiteId = self.siteId.data).first()
		if area:
			if self.areaId.data == "":
				# Trying to add a new area using an abbreviation that already exists.
				validationError = True
			else:
				if int(self.areaId.data) != area.AreaId:
					# Trying to change the abbreviation of a area to an abbreviation that already exists.
					validationError = True

		if validationError:
			raise ValidationError('The abbreviation "{}" already exists.'.format(field.data))

	def validate_name(self, field):
		validationError = False
		area = Area.query.filter_by(SiteId = self.siteId.data, Name = field.data).first()
		if area:
			if self.areaId.data == "":
				# Trying to add a new area using a name that already exists.
				validationError = True
			else:
				if int(self.areaId.data) != area.AreaId:
					# Trying to change the name of a area to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
