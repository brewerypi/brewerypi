from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Length 
from .. models import Site

class SiteForm(FlaskForm):
	name = StringField("Name", validators = [DataRequired(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators = [DataRequired(), Length(1, 10)])
	description = StringField("Description", validators = [Length(0, 255)])
	siteId = HiddenField()
	enterpriseId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_abbreviation(self, field):
		validationError = False
		site = Site.query.filter_by(Abbreviation = field.data, EnterpriseId = self.enterpriseId.data).first()
		if site:
			if self.siteId.data == "":
				# Trying to add a new site using an abbreviation that already exists.
				validationError = True
			else:
				if int(self.siteId.data) != site.SiteId:
					# Trying to change the abbreviation of a site to an abbreviation that already exists.
					validationError = True

		if validationError:
			raise ValidationError('The abbreviation "{}" already exists.'.format(field.data))

	def validate_name(self, field):
		validationError = False
		site = Site.query.filter_by(EnterpriseId = self.enterpriseId.data, Name = field.data).first()
		if site:
			if self.siteId.data == "":
				# Trying to add a new site using a name that already exists.
				validationError = True
			else:
				if int(self.siteId.data) != site.SiteId:
					# Trying to change the name of a site to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))
