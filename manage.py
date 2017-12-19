import os
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from app import create_app, db
from app . models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Lookup, LookupValue, \
	Site, Tag, TagValue, UnitOfMeasurement

app = create_app(os.getenv("FLASK_CONFIG") or "default")
manager = Manager(app)
migrate = Migrate(app, db, directory = "db/migrations")

def make_shell_context():
	return dict(app = app, db = db, Area = Area, AttributeTemplate = AttributeTemplate, Element = Element, ElementAttribute = ElementAttribute, \
		ElementTemplate = ElementTemplate, Enterprise = Enterprise, EventFrame = EventFrame, EventFrameTemplate = EventFrameTemplate, \
		Lookup = Lookup, LookupValue = LookupValue, Site = Site, Tag = Tag, TagValue = TagValue, UnitOfMeasurement = UnitOfMeasurement)

manager.add_command("shell", Shell(make_context = make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == "__main__":
	manager.run()
