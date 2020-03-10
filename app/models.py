import json
from datetime import datetime
from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import func, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.mysql import DOUBLE
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from . import loginManager

class AnonymousUser(AnonymousUserMixin):
	def can(self, permissions):
		return False
	
	def isAdministrator(self):
		return False

loginManager.anonymous_user = AnonymousUser

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

	ManagedElements = db.relationship("Element", backref = "Area", lazy = "dynamic")
	Tags = db.relationship("Tag", backref = "Area", lazy = "dynamic")

	def __repr__(self):
		return "<Area: {}>".format(self.Name)

	def delete(self):
		tags = self.Tags
		for tag in tags:
			tag.delete()
		
		db.session.delete(self)

	def id(self):
		return self.AreaId

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
	TagAreaId = db.Column(db.Integer, db.ForeignKey("Area.AreaId", name = "FK__Area$House$ManagedElementTag"), nullable = True)

	ElementAttributes = db.relationship("ElementAttribute", backref = "Element", lazy = "dynamic")
	EventFrameAttributes = db.relationship("EventFrameAttribute", backref = "Element", lazy = "dynamic")
	EventFrames = db.relationship("EventFrame", backref = "Element", lazy = "dynamic")

	def __repr__(self):
		return "<Element: {}>".format(self.Name)		

	def delete(self):
		elementAttributes = self.ElementAttributes
		for elementAttribute in elementAttributes:
			elementAttribute.delete()

		eventFrames = self.EventFrames
		for eventFrame in eventFrames:
			eventFrame.delete()

		eventFrameAttributes = self.EventFrameAttributes
		for eventFrameAttribute in eventFrameAttributes:
			eventFrameAttribute.delete()
		
		db.session.delete(self)

	def id(self):
		return self.ElementId

	def isManaged(self):
		return True if self.TagAreaId is not None else False

class ElementAttribute(db.Model):
	__tablename__ = "ElementAttribute"
	__table_args__ = \
	(
		UniqueConstraint("ElementAttributeTemplateId", "ElementId", name = "AK__ElementAttributeTemplateId__ElementId"),
	)

	ElementAttributeId = db.Column(db.Integer, primary_key = True)
	ElementAttributeTemplateId = db.Column(db.Integer, db.ForeignKey("ElementAttributeTemplate.ElementAttributeTemplateId", 
		name = "FK__ElementAttributeTemplate$Have$ElementAttribute"), nullable = False)
	ElementId = db.Column(db.Integer, db.ForeignKey("Element.ElementId", name = "FK__Element$Have$ElementAttribute"), nullable = False)
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId", name = "FK__Tag$Have$ElementAttribute"), nullable = False)

	def delete(self):
		db.session.delete(self)
	
	def id(self):
		return self.ElementAttributeId

class ElementAttributeTemplate(db.Model):
	__tablename__ = "ElementAttributeTemplate"
	__table_args__ = \
	(
		UniqueConstraint("ElementTemplateId", "Name", name = "AK__ElementTemplateId__Name"),
	)

	ElementAttributeTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId", name = "FK__ElementTemplate$Have$ElementAttributeTemplate"), \
		nullable = False)
	LookupId = db.Column(db.Integer, db.ForeignKey("Lookup.LookupId", name = "FK__Lookup$CanBeUsedIn$ElementAttributeTemplate"), nullable = True)
	Name = db.Column(db.String(45), nullable = False)
	UnitOfMeasurementId = db.Column(db.Integer, db.ForeignKey("UnitOfMeasurement.UnitOfMeasurementId", \
		name = "FK__UnitOfMeasurement$CanBeUsedIn$ElementAttributeTemplate"), nullable = True)

	ElementAttributes = db.relationship("ElementAttribute", backref = "ElementAttributeTemplate", lazy = "dynamic")

	def __repr__(self):
		return "<ElementAttributeTemplate: {}>".format(self.Name)

	def delete(self):
		elementAttributes = self.ElementAttributes
		for elementAttribute in elementAttributes:
			elementAttribute.delete()

		db.session.delete(self)

	def id(self):
		return self.ElementAttributeTemplateId

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

	ElementAttributeTemplates = db.relationship("ElementAttributeTemplate", backref = "ElementTemplate", lazy = "dynamic")
	Elements = db.relationship("Element", backref = "ElementTemplate", lazy = "dynamic")
	EventFrameTemplates = db.relationship("EventFrameTemplate", backref = "ElementTemplate", lazy = "dynamic")

	def __repr__(self):
		return "<ElementTemplate: {}>".format(self.Name)

	def delete(self):
		elementAttributeTemplates = self.ElementAttributeTemplates
		for elementAttributeTemplate in elementAttributeTemplates:
			elementAttributeTemplate.delete()

		elements = self.Elements
		for element in elements:
			element.delete()

		eventFrameTemplates = self.EventFrameTemplates
		for eventFrameTemplate in eventFrameTemplates:
			eventFrameTemplate.delete()
		
		db.session.delete(self)

	def id(self):
		return self.ElementTemplateId

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

	def delete(self):
		lookups = self.Lookups
		for lookup in lookups:
			lookup.delete()

		sites = self.Sites
		for site in sites:
			site.delete()

		db.session.delete(self)

	def id(self):
		return self.EnterpriseId

class EventFrame(db.Model):
	__tablename__ = "EventFrame"
	__table_args__ = \
	(
		Index("IX__StartTimestamp__EndTimestamp", "StartTimestamp", "EndTimestamp"),
		UniqueConstraint("ElementId", "EventFrameTemplateId", "StartTimestamp", name = "AK__ElementId_EventFrameTemplateId_StartTimestamp"),
	)

	EventFrameId = db.Column(db.Integer, primary_key = True)
	ElementId = db.Column(db.Integer, db.ForeignKey("Element.ElementId", name = "FK__Element$Have$EventFrame"), nullable = True)
	EndTimestamp = db.Column(db.DateTime, nullable = True)
	EventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId", name = "FK__EventFrameTemplate$Have$EventFrame"), \
		nullable = False)
	Name = db.Column(db.String(45), nullable = False)
	ParentEventFrameId = db.Column(db.Integer, db.ForeignKey("EventFrame.EventFrameId", name = "FK__EventFrame$CanHave$ParentEventFrame"), nullable = True)
	SourceEventFrameId = db.Column(db.Integer, db.ForeignKey("EventFrame.EventFrameId", name = "FK__EventFrame$CanHave$SourceEventFrame"), nullable = True)
	StartTimestamp = db.Column(db.DateTime, nullable = False)
	UserId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$AddOrEdit$EventFrame"), nullable = False)

	ParentEventFrame = db.relationship("EventFrame", foreign_keys = [ParentEventFrameId], remote_side = [EventFrameId])
	ChildEventFrames = db.relationship("EventFrame", foreign_keys = [ParentEventFrameId], remote_side = [ParentEventFrameId])
	SourceEventFrame = db.relationship("EventFrame", foreign_keys = [SourceEventFrameId], remote_side = [EventFrameId])
	DestinationEventFrames = db.relationship("EventFrame", foreign_keys = [SourceEventFrameId], remote_side = [SourceEventFrameId])
	EventFrameNotes = db.relationship("EventFrameNote", backref = "EventFrame", lazy = "dynamic")

	def __repr__(self):
		return "<EventFrame: {}>".format(self.Name)

	def ancestors(self, ancestors):
		if self.ParentEventFrameId == None:
			return ancestors
		else:
			ancestors.insert(0, self.ParentEventFrame)
			return self.ParentEventFrame.ancestors(ancestors)

	def delete(self):
		eventFrameNotes = self.EventFrameNotes
		for eventFrameNote in eventFrameNotes:
			eventFrameNote.delete()

		childEventFrames = self.ChildEventFrames
		for childEventFrame in childEventFrames:
			childEventFrame.delete()

		db.session.delete(self)

	def hasDescendants(self):
		if self.ChildEventFrames:
			return True
		else:
			return False

	def id(self):
		return self.EventFrameId

	def qualifiedName(self):
		ancestors = self.ancestors([])
		ancestry = ""
		for ancestor in ancestors:
			ancestry = "{}_{}".format(ancestry, ancestor.Name) if ancestry else "{}".format(ancestor.Name)
		
		elementTemplate = self.origin().EventFrameTemplate.ElementTemplate
		if ancestry:
			qualifiedName = "{}_{}_{}_{}_{}".format(elementTemplate.Site.Enterprise.Abbreviation, elementTemplate.Site.Abbreviation, 
				self.origin().Element.Name, ancestry, self.Name)
		else:
			qualifiedName = "{}_{}_{}_{}".format(elementTemplate.Site.Enterprise.Abbreviation, elementTemplate.Site.Abbreviation, self.Element.Name, self.Name)

		return qualifiedName

	def origin(self):
		if self.ParentEventFrameId == None:
			return self
		else:
			return self.ParentEventFrame.origin()

class EventFrameAttribute(db.Model):
	__tablename__ = "EventFrameAttribute"
	__table_args__ = \
	(
		UniqueConstraint("EventFrameAttributeTemplateId", "ElementId", name = "AK__EventFrameAttributeTemplateId__ElementId"),
	)

	EventFrameAttributeId = db.Column(db.Integer, primary_key = True)
	ElementId = db.Column(db.Integer, db.ForeignKey("Element.ElementId", name = "FK__Element$Have$EventFrameAttribute"), nullable = False)
	EventFrameAttributeTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameAttributeTemplate.EventFrameAttributeTemplateId", 
		name = "FK__EventFrameAttributeTemplate$Have$EventFrameAttribute"), nullable = False)
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId", name = "FK__Tag$Have$EventFrameAttribute"), nullable = False)

	def __repr__(self):
		return "<EventFrameAttribute: {} - {} - {}>".format(self.Element.Name, self.EventFrameAttributeTemplate.Name, self.Tag.Name)

	def delete(self):
		db.session.delete(self)

	def id(self):
		return self.EventFrameAttributeId

class EventFrameAttributeTemplate(db.Model):
	__tablename__ = "EventFrameAttributeTemplate"
	__table_args__ = \
	(
		UniqueConstraint("EventFrameTemplateId", "Name", name = "AK__EventFrameTemplateId__Name"),
	)

	EventFrameAttributeTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	DefaultEndValue = db.Column(db.Float, nullable = True)
	DefaultStartValue = db.Column(db.Float, nullable = True)
	EventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId", \
		name = "FK__EventFrameTemplate$Have$EventFrameAttributeTemplate"), nullable = False)
	LookupId = db.Column(db.Integer, db.ForeignKey("Lookup.LookupId", name = "FK__Lookup$CanBeUsedIn$EventFrameAttributeTemplate"), nullable = True)
	Name = db.Column(db.String(45), nullable = False)
	UnitOfMeasurementId = db.Column(db.Integer, db.ForeignKey("UnitOfMeasurement.UnitOfMeasurementId", \
		name = "FK__UnitOfMeasurement$CanBeUsedIn$EventFrameAttributeTemplate"), nullable = True)

	EventFrameAttributes = db.relationship("EventFrameAttribute", backref = "EventFrameAttributeTemplate", lazy = "dynamic")

	def __repr__(self):
		return "<EventFrameAttributeTemplate: {}>".format(self.Name)

	def delete(self):
		eventFrameAttributes = self.EventFrameAttributes
		for eventFrameAttribute in eventFrameAttributes:
			eventFrameAttribute.delete()

		db.session.delete(self)

	def id(self):
		return self.EventFrameAttributeTemplateId

	def path(self):
		path = ""
		for ancestor in self.EventFrameTemplate.ancestors([]):
			path += "\{}".format(ancestor.Name)
		return  "{}\{}".format(path, self.EventFrameTemplate.Name)

class EventFrameNote(db.Model):
	__tablename__ = "EventFrameNote"
	__table_args__ = \
	(
		PrimaryKeyConstraint("NoteId", "EventFrameId"),
	)

	EventFrameId = db.Column(db.Integer, db.ForeignKey("EventFrame.EventFrameId", name = "FK__EventFrame$CanHave$EventFrameNote"), nullable = False)
	NoteId = db.Column(db.Integer, db.ForeignKey("Note.NoteId", name = "FK__Note$CanBe$EventFrameNote"), nullable = False)

	def delete(self):
		note = Note.query.get(self.NoteId)
		db.session.delete(note)
		db.session.delete(self)

class EventFrameTemplate(db.Model):
	__tablename__ = "EventFrameTemplate"
	__table_args__ = \
	(
		UniqueConstraint("ElementTemplateId", "Name", name = "AK__ElementTemplateId_Name"),
		UniqueConstraint("Name", "ParentEventFrameTemplateId", name = "AK__Name_ParentEventFrameTemplateId"),
		UniqueConstraint("Order", "ParentEventFrameTemplateId", name = "AK__Order_ParentEventFrameTemplateId"),
	)

	EventFrameTemplateId = db.Column(db.Integer, primary_key = True)
	Description = db.Column(db.String(255), nullable = True)
	ElementTemplateId = db.Column(db.Integer, db.ForeignKey("ElementTemplate.ElementTemplateId", name = "FK__ElementTemplate$Have$EventFrameTemplate"), \
		nullable = True)
	Name = db.Column(db.String(45), nullable = False)
	Order = db.Column(db.Integer, nullable = False)
	ParentEventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId",
		name = "FK__EventFrameTemplate$CanHave$ParentEventFrameTemplate"), nullable = True)

	EventFrameAttributeTemplates = db.relationship("EventFrameAttributeTemplate", backref = "EventFrameTemplate", lazy = "dynamic")
	EventFrames = db.relationship("EventFrame", backref = "EventFrameTemplate", lazy = "dynamic")
	ParentEventFrameTemplate = db.relationship("EventFrameTemplate", foreign_keys = [ParentEventFrameTemplateId], remote_side = [EventFrameTemplateId])
	ChildEventFrameTemplates = db.relationship("EventFrameTemplate", foreign_keys = [ParentEventFrameTemplateId], remote_side = [ParentEventFrameTemplateId])
	
	def __repr__(self):
		return "<EventFrameTemplate: {}>".format(self.Name)

	def ancestors(self, ancestors):
		if self.ParentEventFrameTemplateId == None:
			return ancestors
		else:
			ancestors.insert(0, self.ParentEventFrameTemplate)
			return self.ParentEventFrameTemplate.ancestors(ancestors)

	def delete(self):
		childEventFrameTemplates = self.ChildEventFrameTemplates
		for childEventFrameTemplate in childEventFrameTemplates:
			childEventFrameTemplate.delete()

		eventFrameAttributeTemplates = self.EventFrameAttributeTemplates
		for eventFrameAttributeTemplate in eventFrameAttributeTemplates:
			eventFrameAttributeTemplate.delete()

		eventFrames = self.EventFrames
		for eventFrame in eventFrames:
			eventFrame.delete()

		db.session.delete(self)

	def qualifiedName(self):
		ancestors = self.ancestors([])
		ancestry = ""
		for ancestor in ancestors:
			ancestry = "{}_{}".format(ancestry, ancestor.Name) if ancestry else "{}".format(ancestor.Name)
		
		elementTemplate = self.origin().ElementTemplate
		if ancestry:
			qualifiedName = "{}_{}_{}_{}_{}".format(elementTemplate.Site.Enterprise.Abbreviation, elementTemplate.Site.Abbreviation, elementTemplate.Name, ancestry, self.Name)
		else:
			qualifiedName = "{}_{}_{}_{}".format(elementTemplate.Site.Enterprise.Abbreviation, elementTemplate.Site.Abbreviation, elementTemplate.Name, self.Name)

		return qualifiedName

	def lineage(self, linealDescent, level):
		linealDescent.append({"eventFrameTemplate" : self, "level" : level})
		if self.hasDescendants():
			descendantEventFrameTemplates = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = self.EventFrameTemplateId). \
				order_by(EventFrameTemplate.Order)
			for descendant in descendantEventFrameTemplates:
				descendant.lineage(linealDescent, level + 1)
		if level == 0:
			return linealDescent

	def hasDescendants(self):
		if self.ChildEventFrameTemplates:
			return True
		else:
			return False

	def hasParent(self):
		if self.ParentEventFrameTemplateId:
			return True
		else:
			return False

	def id(self):
		return self.EventFrameTemplateId

	def origin(self):
		if self.ParentEventFrameTemplateId == None:
			return self
		else:
			return self.ParentEventFrameTemplate.origin()	

class Lookup(db.Model):
	__tablename__ = "Lookup"
	__table_args__ = \
	(
		UniqueConstraint("EnterpriseId", "Name", name = "AK__EnterpriseId__Name"),
	)

	LookupId = db.Column(db.Integer, primary_key = True)
	EnterpriseId = db.Column(db.Integer, db.ForeignKey("Enterprise.EnterpriseId", name = "FK__Enterprise$Have$Lookup"), nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	ElementAttributeTemplates = db.relationship("ElementAttributeTemplate", backref = "Lookup", lazy = "dynamic")
	EventFrameAttributeTemplates = db.relationship("EventFrameAttributeTemplate", backref = "Lookup", lazy = "dynamic")
	LookupValues = db.relationship("LookupValue", backref = "Lookup", lazy = "dynamic")
	Tags = db.relationship("Tag", backref = "Lookup", lazy = "dynamic")

	def __repr__(self):
		return "<Lookup: {}>".format(self.Name)

	def delete(self):
		lookupValues = self.LookupValues
		for lookupValue in lookupValues:
			lookupValue.delete()

		db.session.delete(self)

	def id(self):
		return self.LookupId

	def isReferenced(self):
		if db.session.query(func.count(EventFrameAttributeTemplate.EventFrameAttributeTemplateId)).filter_by(LookupId = self.LookupId).scalar() > 0:
			return True
		elif db.session.query(func.count(ElementAttributeTemplate.ElementAttributeTemplateId)).filter_by(LookupId = self.LookupId).scalar() > 0:
			return True
		elif db.session.query(func.count(Tag.TagId)).filter_by(LookupId = self.LookupId).scalar() > 0:
			return True
		else:
			return False		

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

	def delete(self):
		db.session.delete(self)

	def id(self):
		return self.LookupValueId

	def isReferenced(self):
		# Event frame attribute template default start value.
		if db.session.query(func.count(EventFrameAttributeTemplate.EventFrameAttributeTemplateId)). \
			join(TagValue, EventFrameAttributeTemplate.DefaultStartValue == self.Value).filter(EventFrameAttributeTemplate.LookupId == self.LookupId). \
			scalar() > 0:
			return True
		# Event frame attribute template default end value.
		elif db.session.query(func.count(EventFrameAttributeTemplate.EventFrameAttributeTemplateId)). \
			join(TagValue, EventFrameAttributeTemplate.DefaultEndValue == self.Value).filter(EventFrameAttributeTemplate.LookupId == self.LookupId). \
			scalar() > 0:
			return True
		# Tag value.
		elif db.session.query(func.count(TagValue.TagValueId)).join(Tag).filter(TagValue.Value == self.Value, Tag.LookupId == self.LookupId).scalar() > 0:
			return True
		else:
			return False

class Message(db.Model):
	__tablename__ = "Message"
	__table_args__ = \
	(
		Index("IX__RecipientId__Timestamp", "RecipientId", "Timestamp"),
	)

	MessageId = db.Column(db.Integer, primary_key = True)
	Body = db.Column(db.Text, nullable = False)
	RecipientId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$Receive$Message"), nullable = False)
	SenderId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$Send$Message"), nullable = False)
	Timestamp = db.Column(db.DateTime, nullable = False, default = datetime.utcnow)

	def __repr__(self):
		return "<Message: {}>".format(self.Body)

	def delete(self):
		db.session.delete(self)

	def id(self):
		return self.MessageId

class Note(db.Model):
	__tablename__ = "Note"
	__table_args__ = \
	(
		Index("IX__Timestamp", "Timestamp"),
	)

	NoteId = db.Column(db.Integer, primary_key = True)
	Note = db.Column(db.Text, nullable = False)
	Timestamp = db.Column(db.DateTime, nullable = False)
	UserId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$AddOrEdit$Note"), nullable = False)
	
	TagValueNotes = db.relationship("TagValueNote", backref = "Note", lazy = "dynamic")
	EventFrameNotes = db.relationship("EventFrameNote", backref = "Note", lazy = "dynamic")

class Notification(db.Model):
	__tablename__ = "Notification"
	__table_args__ = \
	(
		Index("IX__UserId__Name__UnixTimestamp", "UserId", "Name", "UnixTimestamp"),
	)

	NotificationId = db.Column(db.Integer, primary_key = True)
	Name = db.Column(db.String(128), nullable = False)
	Payload = db.Column(db.Text)
	UnixTimestamp = db.Column(DOUBLE(asdecimal = False), nullable = False, default = time)
	UserId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$Have$Notification"), nullable = False)

	def getPayload(self):
		return json.loads(self.Payload)

class Permission:
	DATA_ENTRY = 0x01
	ADMINISTER = 0x80

class Role(db.Model):
	__tablename__ = "Role"
	__table_args__ = \
	(
		UniqueConstraint("Name", name = "AK__Name"),
		Index("IX__Name", "Name"),
	)

	RoleId = db.Column(db.Integer, primary_key = True)
	Name = db.Column(db.String(45), nullable = False)
	Permissions = db.Column(db.Integer)	

	Users = db.relationship("User", backref = "Role", lazy = "dynamic")

	@staticmethod
	def insertDefaultRoles():
		defaultRoles = {"User" : Permission.DATA_ENTRY, "Administrator" : 0xff}
		for defaultRole in defaultRoles:
			role = Role.query.filter_by(Name = defaultRole).first()
			if role is None:
				role = Role(Name = defaultRole)
			role.Permissions = defaultRoles[defaultRole]
			db.session.add(role)
		db.session.commit()

	def __repr__(self):
		return "<Role: {}>".format(self.Name)

	def id(self):
		return self.RoleId

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

	def delete(self):
		areas = self.Areas
		for area in areas:
			area.delete()

		elementTemplates = self.ElementTemplates
		for elementTemplate in elementTemplates:
			elementTemplate.delete()

		db.session.delete(self)

	def id(self):
		return self.SiteId

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
	EventFrameAttributes = db.relationship("EventFrameAttribute", backref = "Tag", lazy = "dynamic")
	TagValues = db.relationship("TagValue", backref = "Tag", lazy = "dynamic")

	def __repr__(self):
		return "<Tag: {}>".format(self.Name)

	def delete(self):
		elementAttributes = self.ElementAttributes
		for elementAttribute in elementAttributes:
			elementAttribute.delete()

		eventFrameAttributes = self.EventFrameAttributes
		for eventFrameAttribute in eventFrameAttributes:
			eventFrameAttribute.delete()

		tagValues = self.TagValues
		for tagValue in tagValues:
			tagValue.delete()

		db.session.delete(self)

	def exists(self):
		return False if Tag.query.filter_by(Name = self.Name, AreaId = self.AreaId).scalar() is None else True

	def fullAbbreviatedPathName(self):
		return "{}_{}_{}_{}".format(self.Area.Site.Enterprise.Abbreviation, self.Area.Site.Abbreviation, self.Area.Abbreviation, self.Name)

	def id(self):
		return self.TagId

	def isReferenced(self):
		if db.session.query(func.count(EventFrameAttribute.EventFrameAttributeId)).filter_by(TagId = self.TagId).scalar() > 0:
			return True
		elif db.session.query(func.count(ElementAttribute.ElementAttributeId)).filter_by(TagId = self.TagId).scalar() > 0:
			return True
		else:
			return False

class TagValue(db.Model):
	__tablename__ = "TagValue"
	__table_args__ = \
	(
		UniqueConstraint("TagId", "Timestamp", name = "AK__TagId__Timestamp"),
		Index("IX__Timestamp", "Timestamp"),
	)

	TagValueId = db.Column(db.Integer, primary_key = True)
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId", name = "FK__Tag$Have$TagValue"), nullable = False)
	Timestamp = db.Column(db.DateTime, nullable = False)
	UserId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$AddOrEdit$TagValue"), nullable = False)
	Value = db.Column(db.Float, nullable = False)

	TagValueNotes = db.relationship("TagValueNote", backref = "TagValue", lazy = "dynamic")

	def __repr__(self):
		return "<TagValue: {}>".format(self.TagId)

	def delete(self):
		tagValuesNotes = self.TagValueNotes
		for tagValueNote in tagValuesNotes:
			tagValueNote.delete()

		db.session.delete(self)

	def id(self):
		return self.TagValueId

class TagValueNote(db.Model):
	__tablename__ = "TagValueNote"
	__table_args__ = \
	(
		PrimaryKeyConstraint("NoteId", "TagValueId"),
	)

	NoteId = db.Column(db.Integer, db.ForeignKey("Note.NoteId", name = "FK__Note$CanBe$TagValueNote"), nullable = False)
	TagValueId = db.Column(db.Integer, db.ForeignKey("TagValue.TagValueId", name = "FK__TagValue$CanHave$TagValueNote"), nullable = False)

	def delete(self):
		note = Note.query.get(self.NoteId)
		db.session.delete(note)
		db.session.delete(self)

class UnitOfMeasurement(db.Model):
	__tablename__ = "UnitOfMeasurement"
	__table_args__ = \
	(
		UniqueConstraint("Abbreviation", "Name", name = "AK__Abbreviation__Name"),
	)

	UnitOfMeasurementId = db.Column(db.Integer, primary_key = True)
	Abbreviation = db.Column(db.String(15), nullable = False)
	Name = db.Column(db.String(45), nullable = False)

	ElementAttributeTemplates = db.relationship("ElementAttributeTemplate", backref = "UnitOfMeasurement", lazy = "dynamic")
	EventFrameAttributeTemplates = db.relationship("EventFrameAttributeTemplate", backref = "UnitOfMeasurement", lazy = "dynamic")
	Tags = db.relationship("Tag", backref = "UnitOfMeasurement", lazy = "dynamic")

	def __repr__(self):
		return "<UnitOfMeasurement: {}>".format(self.Name)

	def delete(self):
		db.session.delete(self)

	def id(self):
		return self.UnitOfMeasurementId

	def isReferenced(self):
		if db.session.query(func.count(EventFrameAttributeTemplate.EventFrameAttributeTemplateId)).filter_by(UnitOfMeasurementId = self.UnitOfMeasurementId). \
			scalar() > 0:
			return True
		elif db.session.query(func.count(ElementAttributeTemplate.ElementAttributeTemplateId)).filter_by(UnitOfMeasurementId = self.UnitOfMeasurementId). \
			scalar() > 0:
			return True
		elif db.session.query(func.count(Tag.TagId)).filter_by(UnitOfMeasurementId = self.UnitOfMeasurementId).scalar() > 0:
			return True
		else:
			return False

class User(UserMixin, db.Model):
	__tablename__ = "User"
	__table_args__ = \
	(
		UniqueConstraint("Name", name = "AK__Name"),
		Index("IX__Name", "Name"),
	)

	UserId = db.Column(db.Integer, primary_key = True)
	Enabled = db.Column(db.Boolean, nullable = False)
	LastMessageReadTimestamp = db.Column(db.DateTime)
	Name = db.Column(db.String(45), nullable = False)
	PasswordHash = db.Column(db.String(128))
	RoleId = db.Column(db.Integer, db.ForeignKey("Role.RoleId", name = "FK__Role$Have$User"), nullable = False)

	EventFrames = db.relationship("EventFrame", backref = "User", lazy = "dynamic")
	MessagesReceived = db.relationship("Message", foreign_keys = "Message.RecipientId", backref = "Recipient", lazy = "dynamic")
	MessagesSent = db.relationship("Message", foreign_keys = "Message.SenderId", backref = "Sender", lazy = "dynamic")
	Notes = db.relationship("Note", backref = "User", lazy = "dynamic")
	Notifications = db.relationship("Notification", backref = "User", lazy = "dynamic")
	TagValues = db.relationship("TagValue", backref = "User", lazy = "dynamic")

	@property
	def Password(self):
		raise AttributeError("Password is not a readable attribute.")
	
	@Password.setter
	def Password(self, password):
		self.PasswordHash = generate_password_hash(password)

	@staticmethod
	def insertDefaultAdministrator():
		user = User.query.filter_by(Name = "pi").first()
		administratorRole = Role.query.filter_by(Name = "Administrator").one_or_none()
		if administratorRole is None:
			print('Administrator role does not exist. Cannot create default admin/"pi" user without it.')
		else:
			if user is None:
				user = User(Enabled = True, Name = "pi", Password = "brewery", Role = administratorRole)
				db.session.add(user)
			else:
				user.Role = administratorRole

			db.session.commit()

	def __repr__(self):
		return "<User: {}>".format(self.Name)

	def addNotification(self, name, data):
		self.Notifications.filter_by(Name = name).delete()
		notification = Notification(Name = name, Payload = json.dumps(data), User = self)
		db.session.add(notification)
		return notification

	def can(self, permissions):
		return self.Role is not None and (self.Role.Permissions & permissions) == permissions

	def delete(self):
		db.session.delete(self)

	def get_id(self):
		return self.UserId

	def id(self):
		return self.UserId

	def isAdministrator(self):
		return self.can(Permission.ADMINISTER)

	def numberOfNewMessages(self):
		lastReadTimestamp = self.LastMessageReadTimestamp or datetime(1900, 1, 1)
		return Message.query.filter(Message.RecipientId == self.UserId, Message.Timestamp > lastReadTimestamp).count()

	def verifyPassword(self, password):
		return check_password_hash(self.PasswordHash, password)

@loginManager.user_loader
def loadUser(id):
	return User.query.get(int(id))
