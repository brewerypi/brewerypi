from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import HiddenField, StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required
from .. models import Lookup, UnitOfMeasurement

class TagForm(FlaskForm):
	areaId = HiddenField()
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	lookup = QuerySelectField("Lookup", query_factory = lambda: Lookup.query.order_by(Lookup.Name), get_label = "Name")
	unitOfMeasurement = QuerySelectField("Unit", query_factory = lambda: UnitOfMeasurement.query. \
		order_by(UnitOfMeasurement.Abbreviation), get_label = "Abbreviation")
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

class TagImportForm(FlaskForm):
	tagsFile = FileField("Tags Import File", validators = [FileRequired(), FileAllowed(["csv"], ".csv files only!")])
	submit = SubmitField("Import")
