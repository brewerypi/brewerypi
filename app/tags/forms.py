from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Length, Required

from .. models import Area, Enterprise, Lookup, Site, UnitOfMeasurement

def areaFullyAbbreviatedPath(area):
	return area.Site.Enterprise.Abbreviation + "_" + area.Site.Abbreviation + "_" + area.Abbreviation

class TagForm(FlaskForm):
	area = QuerySelectField(query_factory = lambda: Area.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation), \
		get_label = areaFullyAbbreviatedPath)
	name = StringField("Name", validators = [Required(), Length(1, 45)])
	description = TextField("Description", validators = [Length(0, 255)])
	lookup = QuerySelectField("Lookup", query_factory = lambda: Lookup.query.order_by(Lookup.Name), get_label = "Name")
	unitOfMeasurement = QuerySelectField(query_factory = lambda: UnitOfMeasurement.query.order_by(UnitOfMeasurement.Abbreviation), \
		get_label = "Abbreviation")
	submit = SubmitField("Save")
