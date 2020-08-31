import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from flask_login import AnonymousUserMixin, current_user, UserMixin
from sqlalchemy import func, Index, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.mysql import DATETIME, DOUBLE, LONGTEXT
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

	def next(self):
		return next(self.nextAndPreviousList(), self)

	def nextAndPreviousList(self):
		return Area.query.filter_by(SiteId = self.SiteId).order_by(Area.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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

	def next(self, isManaged = False):
		return next(self.nextAndPreviousList(isManaged), self)

	def nextAndPreviousList(self, isManaged):
		if isManaged is True:
			return Element.query.filter_by(TagAreaId = self.TagAreaId, ElementTemplateId = self.ElementTemplateId).order_by(Element.Name).all()
		else:
			return Element.query.filter_by(ElementTemplateId = self.ElementTemplateId).order_by(Element.Name).all()

	def previous(self, isManaged = False):
		return previous(self.nextAndPreviousList(isManaged), self)

	def attributeValues(self, startTimestamp, endTimestamp):
		attributeValues = {}
		elementAttributeTemplateIds = [elementAttributeTemplate.ElementAttributeTemplateId for elementAttributeTemplate in
			self.ElementTemplate.ElementAttributeTemplates]
		elementAttributes = ElementAttribute.query.filter(ElementAttribute.ElementId == self.ElementId,
			ElementAttribute.ElementAttributeTemplateId.in_(elementAttributeTemplateIds))
		for elementAttribute in elementAttributes:
			attributeValues[elementAttribute.ElementAttributeTemplate.Name] = TagValue.query.filter(TagValue.TagId == elementAttribute.TagId,
				TagValue.Timestamp >= startTimestamp, TagValue.Timestamp <= endTimestamp)

		return attributeValues

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

	def next(self):
		return next(self.nextAndPreviousList(), self)
	
	def nextAndPreviousList(self):
		return ElementAttribute.query.join(ElementAttributeTemplate).filter(ElementAttribute.ElementId == self.ElementId). \
			order_by(ElementAttributeTemplate.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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

	def next(self):
		return next(self.nextAndPreviousList(), self)
	
	def nextAndPreviousList(self):
		return ElementTemplate.query.filter_by(SiteId = self.SiteId).order_by(ElementTemplate.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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

	def next(self):
		return next(self.nextAndPreviousList(), self)
	
	def nextAndPreviousList(self):
		return Enterprise.query.order_by(Enterprise.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

class EventFrame(db.Model):
	__tablename__ = "EventFrame"
	__table_args__ = \
	(
		Index("IX__StartTimestamp__EndTimestamp", "StartTimestamp", "EndTimestamp"),
		UniqueConstraint("ElementId", "EventFrameTemplateId", "StartTimestamp", name = "AK__ElementId_EventFrameTemplateId_StartTimestamp"),
	)

	EventFrameId = db.Column(db.Integer, primary_key = True)
	ElementId = db.Column(db.Integer, db.ForeignKey("Element.ElementId", name = "FK__Element$Have$EventFrame"), nullable = True)
	EndTimestamp = db.Column(DATETIME(fsp = 6), nullable = True)
	EventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId", name = "FK__EventFrameTemplate$Have$EventFrame"), \
		nullable = False)
	Name = db.Column(db.String(45), nullable = False)
	ParentEventFrameId = db.Column(db.Integer, db.ForeignKey("EventFrame.EventFrameId", name = "FK__EventFrame$CanHave$EventFrame"), nullable = True)
	StartTimestamp = db.Column(DATETIME(fsp = 6), nullable = False)
	UserId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$AddOrEdit$EventFrame"), nullable = False)

	ParentEventFrame = db.relationship("EventFrame", remote_side = [EventFrameId])
	EventFrameEventFrameGroups = db.relationship("EventFrameEventFrameGroup", backref = "EventFrame", lazy = "dynamic")
	EventFrames = db.relationship("EventFrame", remote_side = [ParentEventFrameId])
	EventFrameNotes = db.relationship("EventFrameNote", backref = "EventFrame", lazy = "dynamic")

	def __repr__(self):
		return "<EventFrame: {}>".format(self.Name)

	def addDefaultAttributeTemplateValues(self, timestamp):
		for eventFrameAttributeTemplate in self.EventFrameTemplate.EventFrameAttributeTemplates:
			if eventFrameAttributeTemplate.DefaultStartValue is not None:
				eventFrameAttribute = EventFrameAttribute.query.filter(EventFrameAttribute.ElementId == self.origin().ElementId,
					EventFrameAttribute.EventFrameAttributeTemplateId == eventFrameAttributeTemplate.EventFrameAttributeTemplateId).one_or_none()
				if eventFrameAttribute is not None:
					tagValue = TagValue(TagId = eventFrameAttribute.TagId, Timestamp = timestamp, UserId = current_user.get_id(),
						Value = eventFrameAttributeTemplate.DefaultStartValue)
					db.session.add(tagValue)

	def ancestors(self, ancestors):
		if self.ParentEventFrameId == None:
			return ancestors
		else:
			ancestors.insert(0, self.ParentEventFrame)
			return self.ParentEventFrame.ancestors(ancestors)

	def delete(self):
		for eventFrameEventFrameGroup in self.EventFrameEventFrameGroups:
			eventFrameEventFrameGroup.delete()

		eventFrameNotes = self.EventFrameNotes
		for eventFrameNote in eventFrameNotes:
			eventFrameNote.delete()

		childEventFrames = self.EventFrames
		for childEventFrame in childEventFrames:
			childEventFrame.delete()

		db.session.delete(self)

	def attributeValues(self, eventFrameTemplateViewId = None, eventFrameAttributeTemplateIds = None):
		eventFrameAttributeValues = {}
		if eventFrameTemplateViewId == -1 or eventFrameAttributeTemplateIds == -1:
			eventFrameAttributeTemplateIds = [eventFrameAttributeTemplate.EventFrameAttributeTemplateId
				for eventFrameAttributeTemplate in self.EventFrameTemplate.EventFrameAttributeTemplates]
		elif eventFrameTemplateViewId is not None:
			eventFrameTemplateView = EventFrameTemplateView.query.get(eventFrameTemplateViewId)
			eventFrameAttributeTemplateIds = [eventFrameAttributeTemplateEventFrameTemplateView.EventFrameAttributeTemplateId
				for eventFrameAttributeTemplateEventFrameTemplateView in eventFrameTemplateView.EventFrameAttributeTemplateEventFrameTemplateViews]
		elif eventFrameAttributeTemplateIds is not None:
			eventFrameAttributeTemplateIds = EventFrameAttributeTemplate.query.with_entities(EventFrameAttributeTemplate.EventFrameAttributeTemplateId). \
				filter(EventFrameAttributeTemplate.EventFrameAttributeTemplateId.in_(eventFrameAttributeTemplateIds)).all()

		eventFrameAttributes = EventFrameAttribute.query.filter(EventFrameAttribute.ElementId == self.ElementId,
			EventFrameAttribute.EventFrameAttributeTemplateId.in_(eventFrameAttributeTemplateIds))
		for eventFrameAttribute in eventFrameAttributes:
			if self.EndTimestamp is None:
				eventFrameAttributeValues[eventFrameAttribute.EventFrameAttributeTemplate.Name] = TagValue.query. \
					filter(TagValue.TagId == eventFrameAttribute.TagId, TagValue.Timestamp >= self.StartTimestamp)
			else:
				eventFrameAttributeValues[eventFrameAttribute.EventFrameAttributeTemplate.Name] = TagValue.query. \
					filter(TagValue.TagId == eventFrameAttribute.TagId, TagValue.Timestamp >= self.StartTimestamp, TagValue.Timestamp <= self.EndTimestamp)

		return eventFrameAttributeValues

	def end(self):
		endTimestamp = datetime.utcnow()
		for dictionary in self.lineage([], 0):
			eventFrame = dictionary["eventFrame"]
			if eventFrame.EndTimestamp is None:
				eventFrame.EndTimestamp = endTimestamp
				eventFrame.UserId = current_user.get_id()
				for eventFrameAttributeTemplate in eventFrame.EventFrameTemplate.EventFrameAttributeTemplates:
					if eventFrameAttributeTemplate.DefaultEndValue is not None:
						eventFrameAttribute = EventFrameAttribute.query.filter(EventFrameAttribute.ElementId == eventFrame.origin().ElementId,
							EventFrameAttribute.EventFrameAttributeTemplateId == eventFrameAttributeTemplate.EventFrameAttributeTemplateId).one_or_none()
						if eventFrameAttribute is not None:
							tagValue = TagValue(TagId = eventFrameAttribute.TagId, Timestamp = endTimestamp, UserId = current_user.get_id(),
								Value = eventFrameAttributeTemplate.DefaultEndValue)
							db.session.add(tagValue)

	def hasDescendants(self):
		if self.EventFrames:
			return True
		else:
			return False

	def id(self):
		return self.EventFrameId

	def lineage(self, linealDescent, level):
		linealDescent.append({"eventFrame" : self, "level" : level})
		if self.hasDescendants():
			descendantEventFrames = EventFrame.query.filter_by(ParentEventFrameId = self.EventFrameId)
			for descendant in descendantEventFrames:
				descendant.lineage(linealDescent, level + 1)
		if level == 0:
			return linealDescent

	def next(self, months):
		return next(self.nextAndPreviousList(months), self)

	def nextAndPreviousList(self, months):
		if months is None:
			# Active event frames only.
			if self.ParentEventFrameId is None:
				return EventFrame.query.filter(EventFrame.EventFrameTemplateId == self.EventFrameTemplateId, EventFrame.EndTimestamp == None). \
					order_by(EventFrame.StartTimestamp.desc()).all()
			else:
				return EventFrame.query.filter(EventFrame.ParentEventFrameId == self.ParentEventFrameId).order_by(EventFrame.StartTimestamp.desc()).all()
		elif months == 0:
			# All event frames.
			if self.ParentEventFrameId is None:
				return EventFrame.query.filter_by(EventFrameTemplateId = self.EventFrameTemplateId).order_by(EventFrame.StartTimestamp.desc()).all()
			else:
				return EventFrame.query.filter_by(ParentEventFrameId = self.ParentEventFrameId).order_by(EventFrame.StartTimestamp.desc()).all()
		else:
			fromTimestamp = datetime.utcnow() - relativedelta(months = months)
			toTimestamp = datetime.utcnow()
			if self.ParentEventFrameId is None:
				return EventFrame.query.filter(EventFrame.EventFrameTemplateId == self.EventFrameTemplateId, EventFrame.StartTimestamp >= fromTimestamp,
					EventFrame.StartTimestamp <= toTimestamp).order_by(EventFrame.StartTimestamp.desc()).all()
			else:
				return EventFrame.query.filter(EventFrame.ParentEventFrameId == self.ParentEventFrameId, EventFrame.StartTimestamp >= fromTimestamp,
					EventFrame.StartTimestamp <= toTimestamp).order_by(EventFrame.StartTimestamp.desc()).all()

	def origin(self):
		if self.ParentEventFrameId == None:
			return self
		else:
			return self.ParentEventFrame.origin()

	def previous(self, months):
		return previous(self.nextAndPreviousList(months), self)

	def restart(self):
		endTimestamp = datetime.utcnow()
		for dictionary in self.lineage([], 0):
			eventFrame = dictionary["eventFrame"]
			if eventFrame.EndTimestamp is not None:
				eventFrame.EndTimestamp = None
				eventFrame.UserId = current_user.get_id()

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

	def next(self):
		return next(self.nextAndPreviousList(), self)

	def nextAndPreviousList(self):
		return EventFrameAttribute.query.join(EventFrameAttributeTemplate).filter(EventFrameAttribute.ElementId == self.ElementId,
			EventFrameAttributeTemplate.EventFrameTemplateId == self.EventFrameAttributeTemplate.EventFrameTemplateId). \
			order_by(EventFrameAttributeTemplate.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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
	EventFrameAttributeTemplateEventFrameTemplateViews = db.relationship("EventFrameAttributeTemplateEventFrameTemplateView",
		backref = "EventFrameAttributeTemplate", lazy = "dynamic")

	def __repr__(self):
		return "<EventFrameAttributeTemplate: {}>".format(self.Name)

	def delete(self):
		for eventFrameAttribute in self.EventFrameAttributes:
			eventFrameAttribute.delete()

		for eventFrameAttributeTemplateEventFrameTemplateView in self.EventFrameAttributeTemplateEventFrameTemplateViews:
			eventFrameAttributeTemplateEventFrameTemplateView.delete()

		db.session.delete(self)

	def id(self):
		return self.EventFrameAttributeTemplateId

	def path(self):
		path = ""
		for ancestor in self.EventFrameTemplate.ancestors([]):
			path += "\{}".format(ancestor.Name)
		return  "{}\{}".format(path, self.EventFrameTemplate.Name)

	def postAddHousekeeping(self, eventFrameTemplate):
		for element in eventFrameTemplate.origin().ElementTemplate.Elements:
			if element.isManaged():
				# Tag management.
				area = Area.query.get_or_404(element.TagAreaId)
				tagName = "{}_{}".format(element.Name, self.Name.replace(" ", ""))
				tag = Tag.query.filter_by(AreaId = area.AreaId, Name = tagName).one_or_none()
				if tag is None:
					# Tag doesn't exist, so create it.
					tag = Tag(AreaId = area.AreaId, Description = "", LookupId = self.LookupId, Name = tagName,
						UnitOfMeasurementId = self.UnitOfMeasurementId)
					db.session.add(tag)
				else:
					# Tag exists, so update LookupId and UnitOfMeasurementId just in case.
					tag.LookupId = self.LookupId
					tag.UnitOfMeasurementId = self.UnitOfMeasurementId

				db.session.commit()

				# Event Frame attribute management.
				eventFrameAttribute = EventFrameAttribute(ElementId = element.ElementId,
					EventFrameAttributeTemplateId = self.EventFrameAttributeTemplateId, TagId = tag.TagId)
				db.session.add(eventFrameAttribute)
				db.session.commit()

		db.session.commit()

		# # Element attribute template management.
		# # Check for an element attribute template from the same element template with the same event frame attribute template name.
		elementAttributeTemplate = ElementAttributeTemplate.query.filter_by(ElementTemplateId = self.EventFrameTemplate.origin().ElementTemplateId,
			Name = self.Name).one_or_none()
		if elementAttributeTemplate is not None:
			# Element attribute template exists, so update Description, LookupId and UnitOfMeasurementId just in case.
			elementAttributeTemplate.Description = self.Description
			elementAttributeTemplate.LookupId = self.LookupId
			elementAttributeTemplate.UnitOfMeasurementId = self.UnitOfMeasurementId
			db.session.commit()

		# Event frame attribute template management.
		# Loop through all event frame template hierarchies checking for an event frame attribute template with the same event frame attribute template name.
		for topLevelEventFrameTemplate in self.EventFrameTemplate.origin().ElementTemplate.EventFrameTemplates:
			for eventFrameTemplate in topLevelEventFrameTemplate.lineage([], 0):
				# Skip the event frame template that is currently being added to.
				if eventFrameTemplate["eventFrameTemplate"].EventFrameTemplateId != self.EventFrameTemplate.EventFrameTemplateId:
					newEventFrameAttributeTemplate = EventFrameAttributeTemplate.query. \
						filter_by(EventFrameTemplateId = eventFrameTemplate["eventFrameTemplate"].EventFrameTemplateId, Name = self.Name).one_or_none()
					if newEventFrameAttributeTemplate is not None:
					# New event frame attribute template exists, so update Description, LookupId and UnitOfMeasurementId just in case.
						newEventFrameAttributeTemplate.Description = self.Description
						newEventFrameAttributeTemplate.LookupId = self.LookupId
						newEventFrameAttributeTemplate.UnitOfMeasurementId = self.UnitOfMeasurementId

		db.session.commit()

class EventFrameAttributeTemplateEventFrameTemplateView(db.Model):
	__tablename__ = "EventFrameAttributeTemplateEventFrameTemplateView"
	__table_args__ = \
	(
		UniqueConstraint("EventFrameAttributeTemplateId", "EventFrameTemplateViewId", name = "AK__EventFrameAttributeTemplateId__EventFrameTemplateViewId"),
		UniqueConstraint("EventFrameTemplateViewId", "Order", name = "AK__EventFrameTemplateViewId__Order"),
	)

	EventFrameAttributeTemplateEventFrameTemplateViewId = db.Column(db.Integer, primary_key = True)
	EventFrameAttributeTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameAttributeTemplate.EventFrameAttributeTemplateId",
		name = "FK__EFAT$Have$EventFrameAttributeTemplateEventFrameTemplateView"), nullable = False)
	EventFrameTemplateViewId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplateView.EventFrameTemplateViewId",
		name = "FK__EFTV$Have$EventFrameAttributeTemplateEventFrameTemplateView"), nullable = False)
	Order = db.Column(db.Integer, nullable = False)

	def delete(self):
		db.session.delete(self)

	def id(self):
		return self.EventFrameAttributeTemplateEventFrameTemplateViewId

class EventFrameEventFrameGroup(db.Model):
	__tablename__ = "EventFrameEventFrameGroup"
	__table_args__ = \
	(
		UniqueConstraint("EventFrameGroupId", "EventFrameId", name = "AK__EventFrameGroupId__EventFrameId"),
	)

	EventFrameEventFrameGroupId = db.Column(db.Integer, primary_key = True)
	EventFrameGroupId = db.Column(db.Integer, db.ForeignKey("EventFrameGroup.EventFrameGroupId", name = "FK__EventFrameGroup$Have$EventFrameEventFrameGroup"),
		nullable = False)
	EventFrameId = db.Column(db.Integer, db.ForeignKey("EventFrame.EventFrameId", name = "FK__EventFrame$Have$EventFrameEventFrameGroup"), nullable = False)

	def delete(self):
		db.session.delete(self)

	def id(self):
		return self.EventFrameEventFrameGroupId

	def next(self):
		return next(self.nextAndPreviousList(), self)
	
	def nextAndPreviousList(self):
		return EventFrameEventFrameGroup.query.join(EventFrame).filter(EventFrameEventFrameGroup.EventFrameGroupId == self.EventFrameGroupId,
			EventFrame.EventFrameTemplateId == self.EventFrame.EventFrameTemplateId).order_by(EventFrame.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

class EventFrameGroup(db.Model):
	__tablename__ = "EventFrameGroup"
	__table_args__ = \
	(
		UniqueConstraint("Name", name = "AK__Name"),
		Index("IX__Name", "Name"),
	)

	EventFrameGroupId = db.Column(db.Integer, primary_key = True)
	Name = db.Column(db.String(45), nullable = False)

	EventFrameEventFrameGroups = db.relationship("EventFrameEventFrameGroup", backref = "EventFrameGroup", lazy = "dynamic")

	def id(self):
		return self.EventFrameGroupId

	def delete(self):
		for eventFrameEventFrameGroup in self.EventFrameEventFrameGroups:
			eventFrameEventFrameGroup.delete()

		db.session.delete(self)

	def next(self):
		return next(self.nextAndPreviousList(), self)
	
	def nextAndPreviousList(self):
		return EventFrameGroup.query.order_by(EventFrameGroup.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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
		name = "FK__EventFrameTemplate$CanHave$EventFrameTemplate"), nullable = True)

	EventFrameAttributeTemplates = db.relationship("EventFrameAttributeTemplate", backref = "EventFrameTemplate", lazy = "dynamic")
	EventFrames = db.relationship("EventFrame", backref = "EventFrameTemplate", lazy = "dynamic")
	EventFrameTemplates = db.relationship("EventFrameTemplate", remote_side = [ParentEventFrameTemplateId])
	EventFrameTemplateViews = db.relationship("EventFrameTemplateView", backref = "EventFrameTemplate", lazy = "dynamic")
	ParentEventFrameTemplate = db.relationship("EventFrameTemplate", remote_side = [EventFrameTemplateId])

	def __repr__(self):
		return "<EventFrameTemplate: {}>".format(self.Name)

	def ancestors(self, ancestors):
		if self.ParentEventFrameTemplateId == None:
			return ancestors
		else:
			ancestors.insert(0, self.ParentEventFrameTemplate)
			return self.ParentEventFrameTemplate.ancestors(ancestors)

	def delete(self):
		childEventFrameTemplates = self.EventFrameTemplates
		for childEventFrameTemplate in childEventFrameTemplates:
			childEventFrameTemplate.delete()

		for eventFrameTemplateView in self.EventFrameTemplateViews:
			eventFrameTemplateView.delete()

		eventFrameAttributeTemplates = self.EventFrameAttributeTemplates
		for eventFrameAttributeTemplate in eventFrameAttributeTemplates:
			eventFrameAttributeTemplate.delete()

		eventFrames = self.EventFrames
		for eventFrame in eventFrames:
			eventFrame.delete()

		db.session.delete(self)

	def hasDescendants(self):
		if self.EventFrameTemplates:
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

	def lineage(self, linealDescent, level):
		linealDescent.append({"eventFrameTemplate" : self, "level" : level})
		if self.hasDescendants():
			descendantEventFrameTemplates = EventFrameTemplate.query.filter_by(ParentEventFrameTemplateId = self.EventFrameTemplateId). \
				order_by(EventFrameTemplate.Order)
			for descendant in descendantEventFrameTemplates:
				descendant.lineage(linealDescent, level + 1)
		if level == 0:
			return linealDescent

	def next(self):
		return next(self.nextAndPreviousList(), self)

	def nextAndPreviousList(self):
		return EventFrameTemplate.query.filter_by(ElementTemplateId = self.ElementTemplateId,
			ParentEventFrameTemplateId = self.ParentEventFrameTemplateId).order_by(EventFrameTemplate.Name).all()

	def origin(self):
		if self.ParentEventFrameTemplateId == None:
			return self
		else:
			return self.ParentEventFrameTemplate.origin()	

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

class EventFrameTemplateView(db.Model):
	__tablename__ = "EventFrameTemplateView"
	__table_args__ = \
	(
		UniqueConstraint("EventFrameTemplateId", "Name", name = "AK__EventFrameTemplateId_Name"),
		UniqueConstraint("EventFrameTemplateViewId", "Order", name = "AK__EventFrameTemplateViewId__Order"),
	)

	EventFrameTemplateViewId = db.Column(db.Integer, primary_key = True)
	Dictionary = db.Column(LONGTEXT, nullable = True)
	Default = db.Column(db.Boolean, nullable = False)
	Description = db.Column(db.String(255), nullable = True)
	EventFrameTemplateId = db.Column(db.Integer, db.ForeignKey("EventFrameTemplate.EventFrameTemplateId",
		name = "FK__EventFrameTemplate$Have$EventFrameTemplateView"), nullable = False)
	Name = db.Column(db.String(45), nullable = False)
	Order = db.Column(db.Integer, nullable = False)
	Selectable = db.Column(db.Boolean, nullable = False)

	EventFrameAttributeTemplateEventFrameTemplateViews = db.relationship("EventFrameAttributeTemplateEventFrameTemplateView",
		backref = "EventFrameTemplateView", lazy = "dynamic")

	def __repr__(self):
		return "<EventFrameTemplateView: {}>".format(self.Name)

	def dictionary(self):
		if self.Dictionary is None or self.Dictionary == "":
			return {}
		else:
			return json.loads(self.Dictionary.replace("'", '"').replace("True", '"True"').replace("False", '"False"'))

	def delete(self):
		for eventFrameAttributeTemplateEventFrameTemplateView in self.EventFrameAttributeTemplateEventFrameTemplateViews:
			eventFrameAttributeTemplateEventFrameTemplateView.delete()

		db.session.delete(self)

	def id(self):
		return self.EventFrameTemplateViewId

	def next(self):
		return next(self.nextAndPreviousList(), self)

	def nextAndPreviousList(self):
		return EventFrameTemplateView.query.filter_by(EventFrameTemplateId = self.EventFrameTemplateId).order_by(EventFrameTemplateView.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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

	def next(self):
		return next(self.nextAndPreviousList(), self)
	
	def nextAndPreviousList(self):
		return Lookup.query.filter_by(EnterpriseId = self.EnterpriseId).order_by(Lookup.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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

	def next(self):
		return next(self.nextAndPreviousList(), self)

	def nextAndPreviousList(self):
		return LookupValue.query.filter_by(LookupId = self.LookupId).order_by(LookupValue.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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
	Timestamp = db.Column(DATETIME(fsp = 6), nullable = False, default = datetime.utcnow)

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
	Timestamp = db.Column(DATETIME(fsp = 6), nullable = False)
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
	
	def next(self):
		return next(self.nextAndPreviousList(), self)

	def nextAndPreviousList(self):
		return Site.query.filter_by(EnterpriseId = self.EnterpriseId).order_by(Site.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

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

	def next(self):
		return next(self.nextAndPreviousList(), self)

	def nextAndPreviousList(self):
		return Tag.query.filter_by(AreaId = self.AreaId).order_by(Tag.Name).all()

	def previous(self):
		return previous(self.nextAndPreviousList(), self)

class TagValue(db.Model):
	__tablename__ = "TagValue"
	__table_args__ = \
	(
		UniqueConstraint("TagId", "Timestamp", name = "AK__TagId__Timestamp"),
		Index("IX__Timestamp", "Timestamp"),
	)

	TagValueId = db.Column(db.Integer, primary_key = True)
	TagId = db.Column(db.Integer, db.ForeignKey("Tag.TagId", name = "FK__Tag$Have$TagValue"), nullable = False)
	Timestamp = db.Column(DATETIME(fsp = 6), nullable = False)
	UserId = db.Column(db.Integer, db.ForeignKey("User.UserId", name = "FK__User$AddOrEdit$TagValue"), nullable = False)
	Value = db.Column(db.Float, nullable = False)

	TagValueNotes = db.relationship("TagValueNote", backref = "TagValue", lazy = "dynamic")

	def __repr__(self):
		return "<TagValue: {}>".format(self.TagValueId)

	def delete(self):
		tagValuesNotes = self.TagValueNotes
		for tagValueNote in tagValuesNotes:
			tagValueNote.delete()

		db.session.delete(self)

	def id(self):
		return self.TagValueId

	def next(self, eventFrameId = None):
		return next(self.nextAndPreviousList(eventFrameId), self)

	def nextAndPreviousList(self, eventFrameId):
		if eventFrameId is None:
			return TagValue.query.filter_by(TagId = self.TagId).order_by(TagValue.Timestamp.desc()).all()
		else:
			eventFrame = EventFrame.query.get_or_404(eventFrameId)
			if eventFrame.EndTimestamp is None:
				return TagValue.query.filter(TagValue.Timestamp >= eventFrame.StartTimestamp, TagValue.TagId == self.TagId).all()
			else:
				return TagValue.query.filter(TagValue.Timestamp <= eventFrame.EndTimestamp, TagValue.Timestamp >= eventFrame.StartTimestamp,
					TagValue.TagId == self.TagId).all()


	def previous(self, eventFrameId = None):
		return previous(self.nextAndPreviousList(eventFrameId), self)

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
	LastMessageReadTimestamp = db.Column(DATETIME(fsp = 6), nullable = True)
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

def next(list, object):
	if list.index(object) + 1 == len(list):
		return list[0]
	else:
		return list[list.index(object) + 1]

def previous(list, object):
	if list.index(object) - 1 == -1:
		return list[len(list) - 1]
	else:
		return list[list.index(object) - 1]
