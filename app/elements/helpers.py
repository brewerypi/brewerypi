from .. import db
from .. models import ElementAttributeTemplate

def elementAttributeValues(elementTemplateId):
    dynamicColumns = ""
    elementAttributeTemplates = ElementAttributeTemplate.query.filter_by(ElementTemplateId = elementTemplateId).order_by(ElementAttributeTemplate.Name)
    for elementAttributeTemplate in elementAttributeTemplates:
        dynamicColumns = dynamicColumns + \
            ", MAX(IF(ElementAttributeTemplate.Name = '{}', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '')) AS '{}'". \
            format(elementAttributeTemplate.Name, elementAttributeTemplate.Name)

    query = """
    SELECT Element.ElementId,
        Element.Name,
        Element.Description,
        Element.TagAreaId,
        Area.Name AS AreaName {}
    FROM Element
        LEFT JOIN Area ON Element.TagAreaId = Area.AreaId
        INNER JOIN ElementTemplate ON Element.ElementTemplateId = ElementTemplate.ElementTemplateId
        LEFT JOIN ElementAttributeTemplate ON ElementTemplate.ElementTemplateId = ElementAttributeTemplate.ElementTemplateId
        LEFT JOIN ElementAttribute ON ElementAttributeTemplate.ElementAttributeTemplateId = ElementAttribute.ElementAttributeTemplateId AND
            Element.ElementId = ElementAttribute.ElementId
        LEFT JOIN
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
            WHERE ElementTemplate.ElementTemplateId = {}
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
    WHERE ElementTemplate.ElementTemplateId = {}
    GROUP BY Element.ElementId
    """.format(dynamicColumns, elementTemplateId, elementTemplateId)
    elements = db.session.execute(query).fetchall()
    return elements
