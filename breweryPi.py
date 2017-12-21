from app import create_app, db
from app . models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, Lookup, LookupValue, Site, Tag, TagValue, \
	UnitOfMeasurement

app = create_app()

@app.shell_context_processor
def make_shell_context():
	return dict(app = app, db = db, Area = Area, AttributeTemplate = AttributeTemplate, Element = Element, ElementAttribute = ElementAttribute, \
		ElementTemplate = ElementTemplate, Enterprise = Enterprise, Lookup = Lookup, LookupValue = LookupValue, Site = Site, Tag = Tag, TagValue = TagValue, \
		UnitOfMeasurement = UnitOfMeasurement)
