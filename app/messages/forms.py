from flask_wtf import FlaskForm
from wtforms import SubmitField, TextAreaField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired
from .. models import User

class MessageForm(FlaskForm):
	recipient = QuerySelectField(query_factory = lambda: User.query.filter_by(Enabled = True).order_by(User.Name), get_label = "Name")
	body = TextAreaField("Message", validators = [DataRequired()])
	submit = SubmitField("Save")
