from app.models import EventFrame, EventFrameAttributeTemplate, EventFrameAttributeTemplateEventFrameTemplateView, EventFrameEventFrameGroup, EventFrameTemplate

def eventFrameAttributeValues(eventFrameGroupId, eventFrameTemplateId, eventFrameTemplateViewId):
	dynamicColumns = ""
	eventFrameIds = [eventFrame.EventFrameId for eventFrame in EventFrame.query.join(EventFrameEventFrameGroup). \
		filter(EventFrame.EventFrameTemplateId == eventFrameTemplateId, EventFrameEventFrameGroup.EventFrameGroupId == eventFrameGroupId)]
	if eventFrameTemplateViewId == -1:
		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.with_entities(EventFrameAttributeTemplate.Name). \
			filter_by(EventFrameTemplateId = eventFrameTemplateId).order_by(EventFrameAttributeTemplate.Name)
	else:
		eventFrameAttributeTemplates = EventFrameAttributeTemplate.query.join(EventFrameAttributeTemplateEventFrameTemplateView). \
			with_entities(EventFrameAttributeTemplate.Name). \
			filter(EventFrameAttributeTemplateEventFrameTemplateView.EventFrameTemplateViewId == eventFrameTemplateViewId). \
			order_by(EventFrameAttributeTemplate.Name)

	for eventFrameAttributeTemplate in eventFrameAttributeTemplates:
		dynamicColumns = dynamicColumns + \
			", MAX(IF(EventFrameAttributeTemplate.Name = '{}', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '')) AS '{}'". \
			format(eventFrameAttributeTemplate.Name, eventFrameAttributeTemplate.Name)

	query = """
		SELECT CONCAT(Enterprise.Abbreviation, '_', Site.Abbreviation, '_', ElementTemplate.Name, '_', EventFrameTemplate.Name) AS Template,
			Element.Name AS Element,
			EventFrame.Name,
			EventFrame.StartTimestamp AS Start,
			EventFrame.EndTimestamp AS End {}
		FROM EventFrame
			INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
			INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
            INNER JOIN ElementTemplate ON Element.ElementTemplateId = ElementTemplate.ElementTemplateId
				AND EventFrameTemplate.ElementTemplateId = ElementTemplate.ElementTemplateId
			INNER JOIN Site ON ElementTemplate.SiteId = Site.SiteId
            INNER JOIN Enterprise ON Site.EnterpriseId = Enterprise.EnterpriseId
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
				WHERE EventFrame.EventFrameId IN ({})
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
		WHERE EventFrame.EventFrameId IN ({})
		GROUP BY EventFrame.EventFrameId
		ORDER BY Template,
			Element
	""".format(dynamicColumns, ",".join(str(eventFrameId) for eventFrameId in eventFrameIds), ",".join(str(eventFrameId) for eventFrameId in eventFrameIds))
	return query
