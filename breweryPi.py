from app import create_app, db
from app . models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, EventFrame, EventFrameNote, EventFrameTemplate, Lookup, LookupValue, Note, Site, Tag, TagValue, TagValueNote, UnitOfMeasurement

app = create_app()

@app.shell_context_processor
def make_shell_context():
	return dict(app = app, db = db, Area = Area, AttributeTemplate = AttributeTemplate, Element = Element, ElementAttribute = ElementAttribute, \
		ElementTemplate = ElementTemplate, Enterprise = Enterprise, EventFrame = EventFrame, EventFrameNote = EventFrameNote, \
		EventFrameTemplate = EventFrameTemplate, Lookup = Lookup, LookupValue = LookupValue, Note = Note, Site = Site, Tag = Tag, TagValue = TagValue, \
		TagValueNote = TagValueNote, UnitOfMeasurement = UnitOfMeasurement)
