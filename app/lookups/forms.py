from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required

from .. models import Enterprise

class LookupForm(FlaskForm):
	enterprise = QuerySelectField(query_factory = lambda: Enterprise.query.order_by(Enterprise.Abbreviation), get_label = "Abbreviation")
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	submit = SubmitField('Save')
