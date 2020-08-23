import click
from flask import current_app
from flask_migrate import Migrate, upgrade
from sqlalchemy import create_engine
from werkzeug.security import generate_password_hash
from app import createApp, db
from app.models import Area, Element, ElementAttribute, ElementAttributeTemplate, ElementTemplate, Enterprise, EventFrame, EventFrameAttribute, \
	EventFrameAttributeTemplate, EventFrameAttributeTemplateEventFrameTemplateView, EventFrameEventFrameGroup, EventFrameGroup, EventFrameNote, \
	EventFrameTemplate, EventFrameTemplateView, Lookup, LookupValue, Message, Permission, Note, Role, Site, Tag, TagValue, TagValueNote, UnitOfMeasurement, User

application = app = createApp()
migrate = Migrate(app, db, directory = "db/migrations")

@app.shell_context_processor
def make_shell_context():
	return dict(app = app, db = db, Area = Area, Element = Element, ElementAttribute = ElementAttribute, ElementAttributeTemplate = ElementAttributeTemplate, 
		ElementTemplate = ElementTemplate, Enterprise = Enterprise, EventFrame = EventFrame, EventFrameAttribute = EventFrameAttribute, 
		EventFrameAttributeTemplate = EventFrameAttributeTemplate,
		EventFrameAttributeTemplateEventFrameTemplateView = EventFrameAttributeTemplateEventFrameTemplateView,
		EventFrameEventFrameGroup = EventFrameEventFrameGroup, EventFrameGroup = EventFrameGroup, EventFrameNote = EventFrameNote,
		EventFrameTemplate = EventFrameTemplate, EventFrameTemplateView = EventFrameTemplateView, Lookup = Lookup, LookupValue = LookupValue, Message = Message,
		Note = Note, Role = Role, Site = Site, Tag = Tag, TagValue = TagValue, TagValueNote = TagValueNote, UnitOfMeasurement = UnitOfMeasurement, User = User)

@app.cli.command(help = "Deploy Brewery Pi database.")
@click.option("--admin", is_flag = True, help = 'Add the default admin ("pi") user. Requires defaults roles.')
@click.option("--roles", is_flag = True, help = "Add the default roles.")
def deploy(admin, roles):
	print ("Creating database {} if it does not exist...".format(current_app.config["MYSQL_DATABASE"]))
	engine = create_engine(current_app.config["SQLALCHEMY_SERVER_URI"])
	connection = engine.connect()
	connection.execute("CREATE DATABASE IF NOT EXISTS {}".format(current_app.config["MYSQL_DATABASE"]))
	print ("Running database upgrade...")
	upgrade()
	if roles == True or admin == True:
		engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])
		connection = engine.connect()
		if roles == True:
			print ("Inserting default roles if needed...")
			connection.execute(f"INSERT INTO `Role` (`Name`, `Permissions`) VALUES ('User', {Permission.DATA_ENTRY})")
			connection.execute(f"INSERT INTO `Role` (`Name`, `Permissions`) VALUES ('Administrator', 0xff)")

		if admin == True:
			print ("Inserting default administrator if needed...")
			administratorRoleId = connection.execute("SELECT RoleId FROM Role WHERE Name = 'Administrator'").scalar()
			if administratorRoleId is None:
				print('Administrator role does not exist. Cannot create default admin/"pi" user without it.')
			else:
				password = generate_password_hash("brewery")
				connection.execute(f"INSERT INTO `User` (`Enabled`, `Name`, `PasswordHash`, `RoleId`) VALUES (1, 'pi', '{password}', {administratorRoleId})")

@app.cli.command(help = "Diplsay Brewery Pi element tree.")
@click.option("--tag-areas", is_flag = True, help = "Show which area(s) element tags belong to.")
def elements(tag_areas):
	print('"*" represents a managed element.')
	enterprises = Enterprise.query.order_by(Enterprise.Name)
	for enterprise in enterprises:
		level = 0
		print(enterprise.Name)
		for site in enterprise.Sites.order_by(Site.Name):
			level = 1
			print("{}{}".format("  " * level, site.Name))
			for elementTemplate in site.ElementTemplates.order_by(ElementTemplate.Name):
				level = 2
				print("{}{}".format("  " * level, elementTemplate.Name))
				for element in elementTemplate.Elements.order_by(Element.Name):
					level = 3
					print("{}{}{}".format("  " * level, element.Name, "" if element.TagAreaId is None else "*"))
					if tag_areas:
						tagAreas = []
						for elementAttribute in element.ElementAttributes:
							if elementAttribute.Tag.Area not in tagAreas:
								tagAreas.append(elementAttribute.Tag.Area)
						tagAreas.sort(key = lambda area: area.Name)
						areas = ""
						for area in tagAreas:
							if areas == "":
								areas = area.Name
							else:
								areas = "{}, ".format(areas) + area.Name
						level = 4
						print("{}Tag area(s): {}".format("  " * level, areas))
