from app.models import Element, ElementAttributeTemplate, ElementTemplate

def elementAttributeValues(elementIds):
    dynamicColumns = ""
    elementAttributeTemplates = Element.query.join(ElementTemplate, ElementAttributeTemplate).with_entities(ElementAttributeTemplate.Name). \
        filter(Element.ElementId.in_(elementIds)).order_by(ElementAttributeTemplate.Name).distinct()
    for elementAttributeTemplate in elementAttributeTemplates:
        dynamicColumns = dynamicColumns + \
            ", MAX(IF(ElementAttributeTemplate.Name = '{}', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '')) AS '{}'". \
            format(elementAttributeTemplate.Name, elementAttributeTemplate.Name)

    query = """
    SELECT Element.Name AS Element,
        ElementTemplate.Name AS Template {}
    FROM Element
        INNER JOIN ElementTemplate ON Element.ElementTemplateId = ElementTemplate.ElementTemplateId
        INNER JOIN ElementAttributeTemplate ON ElementTemplate.ElementTemplateId = ElementAttributeTemplate.ElementTemplateId
        LEFT JOIN ElementAttribute ON ElementAttributeTemplate.ElementAttributeTemplateId = ElementAttribute.ElementAttributeTemplateId AND
            Element.ElementId = ElementAttribute.ElementId
        INNER JOIN
        (
            SELECT Element.ElementId AS ElementId,
                ElementAttributeTemplate.Name AS ElementAttributeTemplateName,
                MAX(TagValue.Timestamp) AS Timestamp
            FROM Element
                INNER JOIN ElementTemplate ON Element.ElementTemplateId = ElementTemplate.ElementTemplateId
                INNER JOIN ElementAttributeTemplate ON ElementTemplate.ElementTemplateId = ElementAttributeTemplate.ElementTemplateId
                LEFT JOIN ElementAttribute ON ElementAttributeTemplate.ElementAttributeTemplateId = ElementAttribute.ElementAttributeTemplateId AND
                    Element.ElementId = ElementAttribute.ElementId
                LEFT JOIN Tag ON ElementAttribute.TagId = Tag.TagId
                LEFT JOIN TagValue TagValue ON Tag.TagId = TagValue.TagId
            WHERE Element.ElementId IN ({})
            GROUP BY ElementId,
                ElementAttributeTemplateName
        ) CurrentElementAttributeValues ON Element.ElementId = CurrentElementAttributeValues.ElementId AND
            ElementAttributeTemplate.Name = CurrentElementAttributeValues.ElementAttributeTemplateName
        LEFT JOIN Tag ON ElementAttribute.TagId = Tag.TagId
        LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId AND
            TagValue.Timestamp = CurrentElementAttributeValues.Timestamp
        LEFT JOIN Lookup ON Tag.LookupId = Lookup.LookupId
        LEFT JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId AND
            TagValue.Value = LookupValue.Value
    WHERE Element.ElementId IN ({})
    GROUP BY Element.ElementId
    ORDER BY Template,
        Element
    """.format(dynamicColumns, ",".join(str(elementId) for elementId in elementIds), ",".join(str(elementId) for elementId in elementIds))
    return query
