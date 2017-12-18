from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Length, Required

class UnitOfMeasurementForm(FlaskForm):
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators = [Required(), Length(1, 15)])
	submit = SubmitField('Save')
