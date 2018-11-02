from flask_wtf import FlaskForm
from datetime import datetime
from wtforms import DateTimeField, HiddenField, SelectField, StringField, SubmitField, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import Required, Optional
from .. models import Element, EventFrame

class EventFrameForm(FlaskForm):
	element = QuerySelectField("Element", validators = [Required()], get_label = "Name")
	eventFrameTemplate = QuerySelectField("Event Frame Template", validators = [Required()], get_label = "Name")
	startTimestamp = DateTimeField("Start Timestamp", default = datetime.now, validators = [Required()])
	endTimestamp = DateTimeField("End Timestamp", validators = [Optional()])
	name = StringField("Name", validators = [Optional()])
	eventFrameTemplateId = HiddenField()
	parentEventFrameId = HiddenField()
	requestReferrer = HiddenField()
	submit = SubmitField("Save")

	# def validate_element(self, field):
	# 	if not self.parentEventFrameId.data and EventFrame.query.filter_by(ElementId = field.data.ElementId, EventFrameTemplateId = self.eventFrameTemplate.data.EventFrameTemplateId, EndTimestamp = None).count() != 0:
	# 		raise ValidationError("There is already an open " + str(self.eventFrameTemplate.data.Name) + " event frame for " + str(field.data.Name) + ".")

	# def validate_eventFrameTemplate(self, field):
	# 	if self.parentEventFrameId.data:
	# 		parentEventFrame = EventFrame.query.get_or_404(self.parentEventFrameId.data)
	# 		# Not sure how to query to filter by parent event frame's element b/c child event frame has ElementId = Null
	# 		# Query written in workbench. How to translate to sqlalchemy?
	# 		if EventFrame.query.filter_by(EventFrameTemplateId = field.data.EventFrameTemplateId, EndTimestamp = None).count() != 0:
	# 			if parentEventFrame.origin().Name:
	# 				strParentEventFrameName = parentEventFrame.origin().Name
	# 			else:
	# 				strParentEventFrameName = parentEventFrame.origin().StartTimestamp + " - " + parentEventFrame.origin().EndTimestamp
	# 			raise ValidationError("There is already an open '" + str(field.data.Name) + "' event frame for " + str(self.element.data.Name) + " under parent event frame '" + strParentEventFrameName + "'.")

	def validate_endTimestamp(self, field):
		if self.endTimestamp.data < self.startTimestamp.data:
			raise ValidationError("The End Timestamp must occur after the Start Timestamp.")

		if self.parentEventFrameId.data:
			parentEventFrame = EventFrame.query.get_or_404(self.parentEventFrameId.data)
			if parentEventFrame.EndTimestamp:
				if self.endTimestamp.data > parentEventFrame.EndTimestamp:
					raise ValidationError("This timestamp is outside of the parent event frame.")

	def validate_startTimestamp(self, field):
		if self.parentEventFrameId.data:
			parentEventFrame = EventFrame.query.get_or_404(self.parentEventFrameId.data)
			error = False
			if parentEventFrame.EndTimestamp:
				if self.startTimestamp.data < parentEventFrame.StartTimestamp or self.startTimestamp.data > parentEventFrame.EndTimestamp:
					error = True
			else:
				if self.startTimestamp.data < parentEventFrame.StartTimestamp:
					error = True

			if error:
				raise ValidationError("This timestamp is outside of the parent event frame.")
