from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField, FileRequired
from wtforms import SubmitField

class DatabaseBackupImportForm(FlaskForm):
	databaseBackupFile = FileField("Database Backup File", validators = [FileRequired(), FileAllowed(["sql"], ".sql files only!")])
	submit = SubmitField("Import")
