from app import create_app, db
from app . models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Lookup, LookupValue, \
	Role, Site, Tag, TagValue, UnitOfMeasurement, User

app = create_app()

@app.shell_context_processor
def make_shell_context():
	return dict(app = app, db = db, Area = Area, AttributeTemplate = AttributeTemplate, Element = Element, ElementAttribute = ElementAttribute,
		ElementTemplate = ElementTemplate, Enterprise = Enterprise, EventFrame = EventFrame, EventFrameTemplate = EventFrameTemplate,
		Lookup = Lookup, LookupValue = LookupValue, Role = Role, Site = Site, Tag = Tag, TagValue = TagValue, UnitOfMeasurement = UnitOfMeasurement,
		User = User)
