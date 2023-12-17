from sqlalchemy import text
from app import db

def areaTags(areaId):
    query = """
    SELECT DISTINCT Tag.TagId,
        Tag.Name,
        Tag.Description,
        Lookup.Name AS LookupName,
        UnitOfMeasurement.Abbreviation AS Unit,
        CASE
            WHEN ElementAttributeElement.TagAreaId IS NULL AND EventFrameAttributeElement.TagAreaId IS NULL THEN FALSE
            ELSE TRUE
        END AS Managed,
        CASE
            WHEN ElementAttribute.TagId IS NULL AND EventFrameAttribute.TagId IS NULL THEN FALSE
            ELSE TRUE
        END AS Referenced
    FROM Tag
        LEFT JOIN Lookup ON Tag.LookupId = Lookup.LookupId
        LEFT JOIN UnitOfMeasurement ON Tag.UnitOfMeasurementId = UnitOfMeasurement.UnitOfMeasurementId
        LEFT JOIN ElementAttribute ON Tag.TagId = ElementAttribute.TagId
        LEFT JOIN Element ElementAttributeElement ON ElementAttribute.ElementId = ElementAttributeElement.ElementId
        LEFT JOIN EventFrameAttribute ON Tag.TagId = EventFrameAttribute.TagId
        LEFT JOIN Element EventFrameAttributeElement ON EventFrameAttribute.ElementId = EventFrameAttributeElement.ElementId
    WHERE Tag.AreaId = {}
    """.format(areaId)
    areaTags = db.session.execute(text(query)).fetchall()
    return areaTags
