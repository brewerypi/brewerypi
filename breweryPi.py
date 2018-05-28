from flask import current_app
from flask_migrate import Migrate, upgrade
from sqlalchemy import create_engine
from app import create_app, db
from app . models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, EventFrame, EventFrameNote, EventFrameTemplate, \
	Lookup, LookupValue, Note, Role, Site, Tag, TagValue, TagValueNote, UnitOfMeasurement, User

app = create_app()
migrate = Migrate(app, db, directory = "db/migrations")

@app.shell_context_processor
def make_shell_context():
	return dict(app = app, db = db, Area = Area, AttributeTemplate = AttributeTemplate, Element = Element, ElementAttribute = ElementAttribute,
		ElementTemplate = ElementTemplate, Enterprise = Enterprise, EventFrame = EventFrame, EventFrameNote = EventFrameNote,
		EventFrameTemplate = EventFrameTemplate, Lookup = Lookup, LookupValue = LookupValue, Note = Note, Role = Role, Site = Site, Tag = Tag,
		TagValue = TagValue, TagValueNote = TagValueNote, UnitOfMeasurement = UnitOfMeasurement, User = User)

@app.cli.command()
def deploy():
	print ("Creating database {} if it does not exist...".format(current_app.config["MYSQL_DATABASE"]))
	engine = create_engine(current_app.config["SQLALCHEMY_SERVER_URI"])
	connection = engine.connect()
	result = connection.execute("CREATE DATABASE IF NOT EXISTS {}".format(current_app.config["MYSQL_DATABASE"]))
	print ("Running database upgrade...")
	upgrade()
	print ("Inserting default roles if needed...")
	Role.insertDefaultRoles()
	print ("Inserting default administrator if needed...")
	User.insertDefaultAdministrator()
	print ("Inserting default units of measurements if needed...")
	UnitOfMeasurement.insertDefaultUnits()
