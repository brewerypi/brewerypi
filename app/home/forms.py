from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from .. models import Area, Enterprise, Site

class DefaultForm(FlaskForm):
	enterprise = QuerySelectField(query_factory = lambda: Enterprise.query.order_by(Enterprise.Name), get_label = "Name")
	site = QuerySelectField(query_factory = lambda: Site.query.order_by(Site.Name), get_label = "Name")
	area = QuerySelectField(query_factory = lambda: Area.query.order_by(Area.Name), get_label = "Name")
	submit = SubmitField("Submit")
