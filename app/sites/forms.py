from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required

from .. models import Enterprise

class SiteForm(FlaskForm):
	enterprise = QuerySelectField(query_factory = lambda: Enterprise.query.order_by(Enterprise.Abbreviation), get_label = "Abbreviation")
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	abbreviation = StringField("Abbreviation", validators = [Required(), Length(1, 10)])
	description = StringField("Description", validators = [Length(0, 255)])
	submit = SubmitField("Save")
