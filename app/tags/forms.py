from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import HiddenField, SelectField, StringField, SubmitField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required
from .. models import Lookup, Tag, UnitOfMeasurement

class TagForm(FlaskForm):
	areaId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	lookup = SelectField("Lookup", validators = [Required()], coerce = int)
	unitOfMeasurement = QuerySelectField("Unit", query_factory = lambda: UnitOfMeasurement.query. \
		order_by(UnitOfMeasurement.Abbreviation), get_label = "Abbreviation")
	tagId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_name(self, field):
		validationError = False
		tag = Tag.query.filter_by(AreaId = self.areaId.data, Name = field.data).first()
		if tag:
			if self.tagId.data == "":
				# Trying to add a new tag using a name that already exists.
				validationError = True
			else:
				if int(self.tagId.data) != tag.TagId:
					# Trying to change the name of a tag to a name that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The name "{}" already exists.'.format(field.data))

class TagImportForm(FlaskForm):
	tagsFile = FileField("Tags Import File", validators = [FileRequired(), FileAllowed(["csv"], ".csv files only!")])
	submit = SubmitField("Import")
