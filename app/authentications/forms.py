from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import Length, Required

class LoginForm(FlaskForm):
    name = StringField("Username", validators = [Length(1, 45), Required()])
    password = PasswordField("Password", validators = [Required()])
    rememberMe = BooleanField("Keep me logged in")
    submit = SubmitField("Log In")
