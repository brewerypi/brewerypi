from sqlalchemy import UniqueConstraint
from app import db

class Area(db.Model):
	__tablename__ = "Area"
	__table_args__ = \
	(
		UniqueConstraint("Abbreviation", "SiteId", name = "AK__Abbreviation__SiteId"),
		UniqueConstraint("Name", "SiteId", name = "AK__Name__SiteId"),
	)

	AreaId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(10), nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	Name = db.Column(db.String(45), nullable = False)
	SiteId = db.Column(db.Integer, db.ForeignKey("Site.SiteId", name = "FK__Site$Have$Area"), nullable = False)

	Tags = db.relationship("Tag", backref = "Area", lazy = "dynamic")

	def __repr__(self):
		return "<Area: {}>".format(self.Name)

class AttributeTemplate(db.Model):
	__tablename__ = "AttributeTemplate"
	__table_args__ = \
	(
		UniqueConstraint("ElementTemplateId", "Name", name = "AK__ElementTemplateId__Name"),
	)

	AttributeTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId", name = "FK__ElementTemplate$Have$AttributeTemplate"), \
		nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	ElementAttributes = db.relationship("ElementAttribute", backref = "AttributeTemplate", lazy = "dynamic")

	def __repr__(self):
		return "<AttributeTemplate: {}>".format(self.Name)

class Element(db.Model):
	__tablename__ = "Element"
	__table_args__ = \
	(
		UniqueConstraint("ElementTemplateId", "Name", name = "AK__ElementTemplateId__Name"),
	)

	ElementId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId", name = "FK__ElementTemplate$Have$Element"), nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	ElementAttributes = db.relationship("ElementAttribute", backref = "Element", lazy = "dynamic")

	def __repr__(self):
		return "<Element: {}>".format(self.Name)

class ElementAttribute(db.Model):
	__tablename__ = "ElementAttribute"
	__table_args__ = \
	(
		UniqueConstraint("AttributeTemplateId", "ElementId", name = "AK__AttributeTemplateId__ElementId"),
	)

	ElementAttributeId = db.Column(db.Integer, primary_key = True)
	AttributeTemplateId = db.Column(db.Integer, db.ForeignKey("AttributeTemplate.AttributeTemplateId", name = "FK__AttributeTemplate$Have$ElementAttribute"), \
		nullable = False)
	ElementId = db.Column(db.Integer, db.ForeignKey("Element.ElementId", name = "FK__Element$Have$ElementAttribute"), nullable = False)
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId", name = "FK__Tag$Have$ElementAttribute"), nullable = False)

class ElementTemplate(db.Model):
	__tablename__ = "ElementTemplate"
	__table_args__ = \
	(
		UniqueConstraint("Name", "SiteId", name = "AK__Name__SiteId"),
	)

	ElementTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	Name = db.Column(db.String(45), nullable = False)
	SiteId = db.Column(db.Integer, db.ForeignKey("Site.SiteId", name = "FK__Site$Have$ElementTemplate"), nullable = False)

	AttributeTemplates = db.relationship("AttributeTemplate", backref = "ElementTemplate", lazy = "dynamic")
	Elements = db.relationship("Element", backref = "ElementTemplate", lazy = "dynamic")
	EventFrameTemplates = db.relationship("EventFrameTemplate", backref = "ElementTemplate", lazy = "dynamic")

	def __repr__(self):
		return "<ElementTemplate: {}>".format(self.Name)

class Enterprise(db.Model):
	__tablename__ = "Enterprise"
	__table_args__ = \
	(
		UniqueConstraint("Abbreviation", name = "AK__Abbreviation"),
		UniqueConstraint("Name", name = "AK__Name"),
	)

	EnterpriseId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(10), nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	Name = db.Column(db.String(45), nullable = False)

	Lookups = db.relationship("Lookup", backref = "Enterprise", lazy = "dynamic")
	Sites = db.relationship("Site", backref = "Enterprise", lazy = "dynamic")

	def __repr__(self):
		return "<Enterprise: {}>".format(self.Name)

class EventFrame(db.Model):
	__tablename__ = "EventFrame"
	__table_args__ = \
	(
		# UniqueConstraint("Name", "ParentEventFrameId", name = "AK__Name_ParentEventFrameId"),
	)

	EventFrameId = db.Column(db.Integer, primary_key = True)
	Name = db.Column(db.String(45), nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	StartTime = db.Column(db.DateTime, nullable = False)
	EndTime = db.Column(db.DateTime, nullable = True)
	ParentEventFrameId = db.Column(db.Integer, db.ForeignKey("EventFrame.EventFrameId", name = "FK__EventFrame$CanHave$EventFrame"), nullable = True)
	EventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId", name = "FK__EventFrameTemplate$Have$EventFrame"), \
		nullable = False)
	Order = db.Column(db.Integer, nullable = False)

	ParentEventFrame = db.relationship("EventFrame", remote_side = [EventFrameId])

	def __repr__(self):
		return "<EventFrame: {}>".format(self.Name)

class EventFrameTemplate(db.Model):
	__tablename__ = "EventFrameTemplate"
	__table_args__ = \
	(
		UniqueConstraint("ElementTemplateId", "Name", "ParentEventFrameTemplateId", name = "AK__ElementTemplateId__Name__ParentEventFrameTemplateId"),
	)

	EventFrameTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId", name = "FK__ElementTemplate$Have$EventFrameTemplate"), \
		nullable = False)
	Name = db.Column(db.String(45), nullable = False)
	ParentEventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId",
		name = "FK__EventFrameTemplate$CanHave$EventFrameTemplate"), nullable = True)

	ParentEventFrameTemplate = db.relationship("EventFrameTemplate", remote_side = [EventFrameTemplateId])
	EventFrames = db.relationship("EventFrame", backref = "EventFrameTemplate", lazy = "dynamic")

	def __repr__(self):
		return "<EventFrameTemplate: {}>".format(self.Name)

class Lookup(db.Model):
	__tablename__ = "Lookup"
	__table_args__ = \
	(
		UniqueConstraint("EnterpriseId", "Name", name = "AK__EnterpriseId__Name"),
	)

	LookupId = db.Column(db.Integer, primary_key = True)
	EnterpriseId = db.Column(db.Integer, db.ForeignKey("Enterprise.EnterpriseId", name = "FK__Enterprise$Have$Lookup"), nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	LookupValues = db.relationship("LookupValue", backref = "Lookup", lazy = "dynamic")
	Tags = db.relationship("Tag", backref = "Lookup", lazy = "dynamic")

	def __repr__(self):
		return "<Lookup: {}>".format(self.Name)

class LookupValue(db.Model):
	__tablename__ = "LookupValue"
	__table_args__ = \
	(
		UniqueConstraint("LookupId", "Name", name = "AK__LookupId__Name"),
		UniqueConstraint("LookupId", "Value", name = "AK__LookupId__Value"),
	)

	LookupValueId = db.Column(db.Integer, primary_key = True)
	Name = db.Column(db.String(45), nullable = False)
	Selectable = db.Column(db.Boolean, nullable = False)
	LookupId = db.Column(db.Integer, db.ForeignKey("Lookup.LookupId", name = "FK__Lookup$Have$LookupValue"), nullable = False)
	Value = db.Column(db.Integer, nullable = False)

	def __repr__(self):
		return "<LookupValue: {}>".format(self.Name)

class Site(db.Model):
	__tablename__ = "Site"
	__table_args__ = \
	(
		UniqueConstraint("Abbreviation", "EnterpriseId", name = "AK__Abbreviation__EnterpriseId"),
		UniqueConstraint("EnterpriseId", "Name", name = "AK__EnterpriseId__Name"),
	)

	SiteId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(10), nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	EnterpriseId = db.Column(db.Integer, db.ForeignKey("Enterprise.EnterpriseId", name = "FK__Enterprise$Have$Site"), nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	Areas = db.relationship("Area", backref = "Site", lazy = "dynamic")
	ElementTemplates = db.relationship("ElementTemplate", backref = "Site", lazy = "dynamic")

	def __repr__(self):
		return "<Site: {}>".format(self.Name)

class Tag(db.Model):
	__tablename__ = "Tag"
	__table_args__ = \
	(
		UniqueConstraint("AreaId", "Name", name = "AK__AreaId__Name"),
	)

	TagId = db.Column(db.Integer, primary_key = True)
	AreaId = db.Column(db.Integer, db.ForeignKey("Area.AreaId", name = "FK__Area$Have$Tag"), nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	LookupId = db.Column(db.Integer, db.ForeignKey("Lookup.LookupId", name = "FK__Lookup$CanBeUsedIn$Tag"), nullable = True)
	Name = db.Column(db.String(45), nullable = False)
	UnitOfMeasurementId = db.Column(db.Integer, db.ForeignKey("UnitOfMeasurement.UnitOfMeasurementId", \
		name = "FK__UnitOfMeasurement$CanBeUsedIn$Tag"), nullable = True)

	ElementAttributes = db.relationship("ElementAttribute", backref = "Tag", lazy = "dynamic")
	TagValues = db.relationship("TagValue", backref = "Tag", lazy = "dynamic")

	def __repr__(self):
		return "<Tag: {}>".format(self.Name)

class TagValue(db.Model):
	__tablename__ = "TagValue"
	__table_args__ = \
	(
		UniqueConstraint("TagId", "Timestamp", name = "AK__TagId__Timestamp"),
	)

	TagValueId = db.Column(db.Integer, primary_key = True)
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId", name = "FK__Tag$Have$TagValue"), nullable = False)
	Timestamp = db.Column(db.DateTime, nullable = False)
	Value = db.Column(db.Float, nullable = False)

	def __repr__(self):
		return "<TagValue: {}>".format(self.TagId)

class UnitOfMeasurement(db.Model):
	__tablename__ = "UnitOfMeasurement"
	__table_args__ = \
	(
		UniqueConstraint("Abbreviation", "Name", name = "AK__Abbreviation__Name"),
	)

	UnitOfMeasurementId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(15), nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	Tags = db.relationship("Tag", backref = "UnitOfMeasurement", lazy = "dynamic")

	def __repr__(self):
		return "<UnitOfMeasurement: {}>".format(self.Name)
