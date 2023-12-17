from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length 

class LoginForm(FlaskForm):
    name = StringField("Username", validators = [DataRequired(), Length(1, 45)])
    password = PasswordField("Password", validators = [DataRequired()])
    rememberMe = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")
