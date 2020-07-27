import click
from flask import current_app
from flask_migrate import Migrate, upgrade
from sqlalchemy import create_engine
from app import createApp, db
from app.models import Area, Element, ElementAttribute, ElementAttributeTemplate, ElementTemplate, Enterprise, EventFrame, EventFrameAttribute, \
	EventFrameAttributeTemplate, EventFrameAttributeTemplateEventFrameTemplateView, EventFrameEventFrameGroup, EventFrameGroup, EventFrameNote, \
	EventFrameTemplate, EventFrameTemplateView, Lookup, LookupValue, Message, Note, Role, Site, Tag, TagValue, TagValueNote, UnitOfMeasurement, User

app = createApp()
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

@app.cli.command()
@click.option("--admin", is_flag = True)
@click.option("--roles", is_flag = True)
def deploy(admin, roles):
	print ("Creating database {} if it does not exist...".format(current_app.config["MYSQL_DATABASE"]))
	engine = create_engine(current_app.config["SQLALCHEMY_SERVER_URI"])
	connection = engine.connect()
	result = connection.execute("CREATE DATABASE IF NOT EXISTS {}".format(current_app.config["MYSQL_DATABASE"]))
	print ("Running database upgrade...")
	upgrade()
	if roles == True:
		print ("Inserting default roles if needed...")
		Role.insertDefaultRoles()

	if admin == True:
		print ("Inserting default administrator if needed...")
		User.insertDefaultAdministrator()

@app.cli.command()
@click.option("--tag-areas", is_flag = True)
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
