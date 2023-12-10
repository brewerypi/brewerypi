from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, FloatField, HiddenField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired
from .. models import TagValue

class TagValueForm(FlaskForm):
	value = FloatField("Value")
	lookupValue = SelectField("Lookup", coerce = float)
	timestamp = DateTimeField("Timestamp", default = datetime.utcnow, validators = [DataRequired()])
	tagValueId = HiddenField()
	tagId = HiddenField()
	utcTimestamp = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	def validate_timestamp(self, field):
		validationError = False
		tagValue = TagValue.query.filter_by(TagId = self.tagId.data, Timestamp = self.utcTimestamp.data).first()
		if tagValue:
			if self.tagValueId.data == "":
				# Trying to add a new tagValue using a timestamp that already exists.
				validationError = True
			else:
				if int(self.tagValueId.data) != tagValue.TagValueId:
					# Trying to change the timestamp of a tagValue to a timestamp that already exists.
					validationError = True
			
		if validationError:
			raise ValidationError('The timestamp "{}" already exists.'.format(field.data))
