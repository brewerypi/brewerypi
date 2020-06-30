from app.models import EventFrameAttributeTemplate, EventFrameTemplate

def activeEventFrameAttributeValues(eventFrameTemplateIds):
    dynamicColumns = ""
    eventFrameAttributeTemplate = EventFrameTemplate.query.join(EventFrameAttributeTemplate).with_entities(EventFrameAttributeTemplate.Name). \
        filter(EventFrameTemplate.EventFrameTemplateId.in_(eventFrameTemplateIds)).order_by(EventFrameAttributeTemplate.Name).distinct()
    for eventFrameAttributeTemplate in eventFrameAttributeTemplate:
        dynamicColumns = dynamicColumns + \
            ", MAX(IF(EventFrameAttributeTemplate.Name = '{}', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '')) AS '{}'". \
            format(eventFrameAttributeTemplate.Name, eventFrameAttributeTemplate.Name)

    query = """
		SELECT EventFrameTemplate.Name AS Template,
			EventFrame.Name,
			Element.Name AS Element,
			EventFrame.StartTimestamp AS Start {}
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
				WHERE EventFrameTemplate.EventFrameTemplateId IN ({}) AND
					EventFrame.EndTimestamp IS NULL
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
		WHERE EventFrameTemplate.EventFrameTemplateId IN ({}) AND
			EventFrame.EndTimestamp IS NULL
		GROUP BY EventFrame.EventFrameId
        ORDER BY Template,
            Element
    """.format(dynamicColumns, ",".join(str(eventFrameTemplateId) for eventFrameTemplateId in eventFrameTemplateIds), ",".join(str(eventFrameTemplateId)
		for eventFrameTemplateId in eventFrameTemplateIds))
    return query
