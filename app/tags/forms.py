from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required
from .. helpers import areaFullyAbbreviatedPath
from .. models import Area, Enterprise, Lookup, Site, UnitOfMeasurement

class TagForm(FlaskForm):
	area = QuerySelectField(query_factory = lambda: Area.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation), \
		get_label = areaFullyAbbreviatedPath)
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = StringField("Description", validators = [Length(0, 255)])
	lookup = QuerySelectField("Lookup", query_factory = lambda: Lookup.query.order_by(Lookup.Name), get_label = "Name")
	unitOfMeasurement = QuerySelectField("Unit", query_factory = lambda: UnitOfMeasurement.query. \
		order_by(UnitOfMeasurement.Abbreviation), get_label = "Abbreviation")
	submit = SubmitField("Save")
