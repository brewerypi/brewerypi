# app/models.py

from sqlalchemy import UniqueConstraint

from app import db

class Area(db.Model):
	__tablename__ = "Area"

	AreaId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(10), unique = True, nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	Name = db.Column(db.String(45), unique = True, nullable = False)
	SiteId = db.Column(db.Integer, db.ForeignKey("Site.SiteId"))

	Tags = db.relationship("Tag", backref = "Area", lazy = "dynamic")

	UniqueConstraint("Name", "SiteId")
	UniqueConstraint("Abbreviation", "SiteId")

	def __repr__(self):
		return "<Area: {}>".format(self.Name)

class AttributeTemplate(db.Model):
	__tablename__ = "AttributeTemplate"

	AttributeTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId"))
	Name = db.Column(db.String(45), unique = True, nullable = False)

	ElementAttributes = db.relationship("ElementAttribute", backref = "AttributeTemplate", lazy = "dynamic")

	UniqueConstraint("ElementTemplateId", "Name")

	def __repr__(self):
		return "<AttributeTemplate: {}>".format(self.Name)

class Element(db.Model):
	__tablename__ = "Element"

	ElementId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId"))
	Name = db.Column(db.String(45), unique = True, nullable = False)

	ElementAttributes = db.relationship("ElementAttribute", backref = "Element", lazy = "dynamic")

	UniqueConstraint("ElementTemplateId", "Name")

	def __repr__(self):
		return "<Element: {}>".format(self.Name)

class ElementAttribute(db.Model):
	__tablename__ = "ElementAttribute"

	ElementAttributeId = db.Column(db.Integer, primary_key = True)
	AttributeTemplateId = db.Column(db.Integer, db.ForeignKey("AttributeTemplate.AttributeTemplateId"))
	ElementId = db.Column(db.Integer, db.ForeignKey("Element.ElementId"))
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId"))

	UniqueConstraint("AttributeTemplateId", "ElementId")

class ElementTemplate(db.Model):
	__tablename__ = "ElementTemplate"

	ElementTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	Name = db.Column(db.String(45), unique = True, nullable = False)
	SiteId = db.Column(db.Integer, db.ForeignKey("Site.SiteId"))

	AttributeTemplates = db.relationship("AttributeTemplate", backref = "ElementTemplate", lazy = "dynamic")
	Elements = db.relationship("Element", backref = "ElementTemplate", lazy = "dynamic")
	EventFrameTemplates = db.relationship("EventFrameTemplate", backref = "ElementTemplate", lazy = "dynamic")

	UniqueConstraint("Name", "SiteId")

	def __repr__(self):
		return "<ElementTemplate: {}>".format(self.Name)

class Enterprise(db.Model):
	__tablename__ = "Enterprise"

	EnterpriseId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(10), unique = True, nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	Name = db.Column(db.String(45), unique = True, nullable = False)

	Lookups = db.relationship("Lookup", backref = "Enterprise", lazy = "dynamic")
	Sites = db.relationship("Site", backref = "Enterprise", lazy = "dynamic")

	def __repr__(self):
		return "<Enterprise: {}>".format(self.Name)

class EventFrame(db.Model):
	__tablename__ = "EventFrame"

	EventFrameId = db.Column(db.Integer, primary_key = True)
	Name = db.Column(db.String(45), unique = True, nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	StartTime = db.Column(db.DateTime, nullable = False)
	EndTime = db.Column(db.DateTime, nullable = True)
	ParentEventFrameId = db.Column(db.Integer, db.ForeignKey("EventFrame.EventFrameId"), nullable = True)
	EventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId"))
	Order = db.Column(db.Integer, unique = True, nullable = False)

	ParentEventFrame = db.relationship("EventFrame", remote_side = [EventFrameId])

	UniqueConstraint("Name", "ParentEventFrameId")
	UniqueConstraint("ParentEventFrameId", "Order")

	def __repr__(self):
		return "<EventFrame: {}>".format(self.Name)

class EventFrameTemplate(db.Model):
	__tablename__ = "EventFrameTemplate"

	EventFrameTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId"))
	Name = db.Column(db.String(45), unique = True, nullable = False)
	ParentEventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId"), nullable = True)

	ParentEventFrameTemplate = db.relationship("EventFrameTemplate", remote_side = [EventFrameTemplateId])
	EventFrames = db.relationship("EventFrame", backref = "EventFrameTemplate", lazy = "dynamic")

	UniqueConstraint("ElementTemplateId", "Name")

	def __repr__(self):
		return "<EventFrameTemplate: {}>".format(self.Name)

class Lookup(db.Model):
	__tablename__ = "Lookup"

	LookupId = db.Column(db.Integer, primary_key = True)
	EnterpriseId = db.Column(db.Integer, db.ForeignKey("Enterprise.EnterpriseId"))
	Name = db.Column(db.String(45), nullable = False)

	LookupValues = db.relationship("LookupValue", backref = "Lookup", lazy = "dynamic")
	Tags = db.relationship("Tag", backref = "Lookup", lazy = "dynamic")

	UniqueConstraint("EnterpriseId", "Name")

	def __repr__(self):
		return "<Lookup: {}>".format(self.Name)

class LookupValue(db.Model):
	__tablename__ = "LookupValue"

	LookupValueId = db.Column(db.Integer, primary_key = True)
	Name = db.Column(db.String(45), unique = True, nullable = False)
	Selectable = db.Column(db.Boolean, nullable = False)
	LookupId = db.Column(db.Integer, db.ForeignKey("Lookup.LookupId"))
	Value = db.Column(db.Integer, nullable = False)

	UniqueConstraint("LookupId", "Name")
	UniqueConstraint("LookupId", "Value")

	def __repr__(self):
		return "<LookupValue: {}>".format(self.Name)

class Site(db.Model):
	__tablename__ = "Site"

	SiteId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(10), nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	EnterpriseId = db.Column(db.Integer, db.ForeignKey("Enterprise.EnterpriseId"))
	Name = db.Column(db.String(45), nullable = False)

	Areas = db.relationship("Area", backref = "Site", lazy = "dynamic")
	ElementTemplates = db.relationship("ElementTemplate", backref = "Site", lazy = "dynamic")

	UniqueConstraint("EnterpriseId", "Name")
	UniqueConstraint("Abbreviation", "EnterpriseId")

	def __repr__(self):
		return "<Site: {}>".format(self.Name)

class Tag(db.Model):
	__tablename__ = "Tag"

	TagId = db.Column(db.Integer, primary_key = True)
	AreaId = db.Column(db.Integer, db.ForeignKey("Area.AreaId"))
	Description = db.Column(db.String(255), nullable = True)
	LookupId = db.Column(db.Integer, db.ForeignKey("Lookup.LookupId"), nullable = True)
	Name = db.Column(db.String(45), nullable = False)
	UnitOfMeasurementId = db.Column(db.Integer, db.ForeignKey("UnitOfMeasurement.UnitOfMeasurementId"))

	ElementAttributes = db.relationship("ElementAttribute", backref = "Tag", lazy = "dynamic")
	TagValues = db.relationship("TagValue", backref = "Tag", lazy = "dynamic")

	UniqueConstraint("AreaId", "Name")

	def __repr__(self):
		return "<Tag: {}>".format(self.Name)

class TagValue(db.Model):
	__tablename__ = "TagValue"

	TagValueId = db.Column(db.Integer, primary_key = True)
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId"))
	Timestamp = db.Column(db.DateTime, nullable = False)
	Value = db.Column(db.Float, nullable = False)

	UniqueConstraint("TagId", "Timestamp")

	def __repr__(self):
		return "<TagValue: {}>".format(self.TagId)

class UnitOfMeasurement(db.Model):
	__tablename__ = "UnitOfMeasurement"

	UnitOfMeasurementId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(15), nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	Tags = db.relationship("Tag", backref = "UnitOfMeasurement", lazy = "dynamic")

	UniqueConstraint("Abbreviation", "Name")

	def __repr__(self):
		return "<UnitOfMeasurement: {}>".format(self.Name)
