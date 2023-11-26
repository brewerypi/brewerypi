from app.models import EventFrameAttributeTemplate, EventFrameAttributeTemplateEventFrameTemplateView

def eventFramesAttributeValues(eventFrameTemplateId, eventFrameTemplateViewId, fromTimestampUtc, toTimestampUtc, activeOnly):
	dynamicColumns = ""
	if eventFrameTemplateViewId == -1:
		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.with_entities(EventFrameAttributeTemplate.Name). \
			filter_by(EventFrameTemplateId = eventFrameTemplateId).order_by(EventFrameAttributeTemplate.Name)
	else:
		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.join(EventFrameAttributeTemplateEventFrameTemplateView). \
			with_entities(EventFrameAttributeTemplate.Name). \
			filter(EventFrameAttributeTemplateEventFrameTemplateView.EventFrameTemplateViewId == eventFrameTemplateViewId). \
			order_by(EventFrameAttributeTemplateEventFrameTemplateView.Order)

	for eventFrameAttributeTemplate in eventFrameAttributeTemplates:
		dynamicColumns = dynamicColumns + \
			", MAX(IF(EventFrameAttributeTemplate.Name = '{}', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '')) AS '{}'". \
			format(eventFrameAttributeTemplate.Name, eventFrameAttributeTemplate.Name)

	query = f"""
		SELECT EventFrame.Name,
			Element.Name AS Element,
			EventFrame.StartTimestamp AS Start,
			EventFrame.EndTimestamp AS End,
			IF(EventFrame.EndTimestamp IS NULL, TIMESTAMPDIFF(SECOND, EventFrame.StartTimestamp, NOW()), TIMESTAMPDIFF(SECOND, EventFrame.StartTimestamp, EventFrame.EndTimestamp)) AS DurationInSeconds {dynamicColumns}
		FROM EventFrame
			INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
			INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
			LEFT JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
			LEFT JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId AND
				Element.ElementId = EventFrameAttribute.ElementId
			LEFT JOIN
			(
				SELECT EventFrame.EventFrameId AS EventFrameId,
					EventFrameAttributeTemplate.Name AS EventFrameAttributeTemplateName,
					MAX(TagValue.Timestamp) AS Timestamp
				FROM EventFrame
					INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
					INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
					INNER JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
					LEFT JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId AND
						Element.ElementId = EventFrameAttribute.ElementId
					LEFT JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
					LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId AND
						CASE
							WHEN EventFrame.EndTimestamp IS NULL THEN
								(TagValue.Timestamp >= EventFrame.StartTimestamp)
							ELSE
								(TagValue.Timestamp >= EventFrame.StartTimestamp AND TagValue.Timestamp <= EventFrame.EndTimestamp)
						END
				WHERE EventFrameTemplate.EventFrameTemplateId = {eventFrameTemplateId} AND
					CASE WHEN {activeOnly} = 1 THEN
						EventFrame.EndTimestamp IS NULL
					ELSE
						EventFrame.StartTimestamp >= '{fromTimestampUtc}' AND
						EventFrame.StartTimestamp <= '{toTimestampUtc}' AND
						EventFrame.EndTimestamp IS NULL OR
						EventFrame.StartTimestamp >= '{fromTimestampUtc}' AND
						EventFrame.EndTimestamp <= '{toTimestampUtc}'
					END
				GROUP BY EventFrameId,
					EventFrameAttributeTemplateName
			) CurrentEventFrameAttributeValue ON EventFrame.EventFrameId = CurrentEventFrameAttributeValue.EventFrameId AND
				EventFrameAttributeTemplate.Name = CurrentEventFrameAttributeValue.EventFrameAttributeTemplateName
			LEFT JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
			LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId AND
				TagValue.Timestamp = CurrentEventFrameAttributeValue.Timestamp
			LEFT JOIN Lookup ON Tag.LookupId = Lookup.LookupId
			LEFT JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId AND
				TagValue.Value = LookupValue.Value
		WHERE EventFrameTemplate.EventFrameTemplateId = {eventFrameTemplateId} AND
			CASE WHEN {activeOnly} = 1 THEN
				EventFrame.EndTimestamp IS NULL
			ELSE
				EventFrame.StartTimestamp >= '{fromTimestampUtc}' AND
				EventFrame.StartTimestamp <= '{toTimestampUtc}' AND
				EventFrame.EndTimestamp IS NULL OR
				EventFrame.StartTimestamp >= '{fromTimestampUtc}' AND
				EventFrame.EndTimestamp <= '{toTimestampUtc}'
			END
		GROUP BY EventFrame.EventFrameId
		ORDER BY Element
	"""
	return query
