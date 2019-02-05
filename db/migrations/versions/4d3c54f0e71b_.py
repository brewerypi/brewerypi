"""empty message

Revision ID: 4d3c54f0e71b
Revises: d35f95abedc4
Create Date: 2019-01-21 22:59:40.557489

"""
from alembic import op
import sqlalchemy as sa
from db.migrations.replaceableObjects import ReplaceableObject


# revision identifiers, used by Alembic.
revision = '4d3c54f0e71b'
down_revision = 'd35f95abedc4'
branch_labels = None
depends_on = None


spActiveEventFrameSummary = ReplaceableObject(
    "spActiveEventFrameSummary",
    "IN eventFrameTemplateIds TEXT, IN eventFrameAttributeTemplateNames TEXT",
    None,
    """
BEGIN
	SET @@group_concat_max_len = 5000;
	SET @sql = NULL;
	SET @dynamicColumns = NULL;

	-- Build the column list of event frame attribute values.
	SELECT GROUP_CONCAT(DISTINCT CONCAT('MAX(IF(EventFrameAttributeTemplate.Name = ''', EventFrameAttributeTemplate.Name, ''', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '''')) AS ''', EventFrameAttributeTemplate.Name, '''')) INTO @dynamicColumns
	FROM EventFrameAttributeTemplate
    WHERE FIND_IN_SET(EventFrameAttributeTemplate.Name, eventFrameAttributeTemplateNames) > 0;

	SET @sql = CONCAT('
		SELECT EventFrameTemplate.Name AS Template,
			EventFrame.Name,
			Element.Name AS Element,
			EventFrame.StartTimestamp AS Start,
            ', @dynamicColumns, '
		FROM EventFrame
			INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
			INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
			INNER JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
			LEFT JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId AND
				Element.ElementId = EventFrameAttribute.ElementId
			INNER JOIN
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
				WHERE EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds, ') AND
					EventFrame.EndTimestamp IS NULL
				GROUP BY EventFrameId,
					EventFrameAttributeTemplateName
			) CurrentEventFrameAttributeValues ON EventFrame.EventFrameId = CurrentEventFrameAttributeValues.EventFrameId AND
				EventFrameAttributeTemplate.Name = CurrentEventFrameAttributeValues.EventFrameAttributeTemplateName
			LEFT JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
			LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId AND
				TagValue.Timestamp = CurrentEventFrameAttributeValues.Timestamp
			LEFT JOIN Lookup ON Tag.LookupId = Lookup.LookupId
			LEFT JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId AND
				TagValue.Value = LookupValue.Value
		WHERE EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds, ') AND
			EventFrame.EndTimestamp IS NULL
		GROUP BY EventFrame.EventFrameId
        ORDER BY Template, Element');

	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END""")


spCurrentEventFrameAttributeValues = ReplaceableObject(
    "spCurrentEventFrameAttributeValues",
    "IN eventFrameIds TEXT, IN eventFrameAttributeTemplateIds TEXT",
    None,
    """
BEGIN
	SET @@group_concat_max_len = 5000;
	SET @sql = NULL;
	SET @dynamicColumns = NULL;

	-- Build the column list of event frame attribute values.
	SELECT GROUP_CONCAT(DISTINCT CONCAT('MAX(IF(EventFrameAttributeTemplate.Name = ''', EventFrameAttributeTemplate.Name, ''', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '''')) AS ''', EventFrameAttributeTemplate.Name, '''')) INTO @dynamicColumns
	FROM EventFrameAttributeTemplate
    WHERE FIND_IN_SET(EventFrameAttributeTemplate.EventFrameAttributeTemplateId, eventFrameAttributeTemplateIds) > 0;

	SET @sql = CONCAT('
		SELECT EventFrame.EventFrameId,
			EventFrame.Name,
			Element.Name,
			EventFrame.StartTimestamp,
            EventFrame.EndTimestamp,
            ', @dynamicColumns, '
		FROM EventFrame
			INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
			INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
			INNER JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
			LEFT JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId AND
				Element.ElementId = EventFrameAttribute.ElementId
			INNER JOIN
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
				WHERE EventFrame.EventFrameId IN (', eventFrameIds ,')
				GROUP BY EventFrameId,
					EventFrameAttributeTemplateName
			) CurrentEventFrameAttributeValues ON EventFrame.EventFrameId = CurrentEventFrameAttributeValues.EventFrameId AND
				EventFrameAttributeTemplate.Name = CurrentEventFrameAttributeValues.EventFrameAttributeTemplateName
			LEFT JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
			LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId AND
				TagValue.Timestamp = CurrentEventFrameAttributeValues.Timestamp
			LEFT JOIN Lookup ON Tag.LookupId = Lookup.LookupId
			LEFT JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId AND
				TagValue.Value = LookupValue.Value
		WHERE EventFrame.EventFrameId IN (', eventFrameIds ,')
		GROUP BY EventFrame.EventFrameId');

	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END""")


spElementSummary = ReplaceableObject(
    "spElementSummary",
    "IN elementAttributeTemplateNames TEXT, IN elementIds TEXT",
    None,
    """
BEGIN
	SET @@group_concat_max_len = 5000;
	SET @sql = NULL;
	SET @dynamicColumns = NULL;

	SELECT GROUP_CONCAT(DISTINCT CONCAT('MAX(IF(ElementAttributeTemplate.Name = ''', ElementAttributeTemplate.Name, ''', IF(Tag.LookupId IS NULL, TagValue.Value, LookupValue.Name), '''')) AS ''', ElementAttributeTemplate.Name, '''')) INTO @dynamicColumns
	FROM ElementAttributeTemplate
    WHERE FIND_IN_SET(ElementAttributeTemplate.Name, elementAttributeTemplateNames) > 0;

	SET @sql = CONCAT('
		SELECT Element.Name AS Element,
			ElementTemplate.Name AS Template,
            ', @dynamicColumns, '
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
				WHERE Element.ElementId IN (', elementIds ,')
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
		WHERE Element.ElementId IN (', elementIds ,')
		GROUP BY Element.ElementId
        ORDER BY Template,
			Element');
	
	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END""")


def upgrade():
	op.replaceStoredProcedure(spActiveEventFrameSummary, replaces = "d35f95abedc4.spActiveEventFrameSummary")
	op.createStoredProcedure(spCurrentEventFrameAttributeValues)
	op.replaceStoredProcedure(spElementSummary, replaces = "ef09d330ca05.spElementSummary")


def downgrade():
	op.replaceStoredProcedure(spElementSummary, replaceWith = "ef09d330ca05.spElementSummary")
	op.dropStoredProcedure(spCurrentEventFrameAttributeValues)
	op.replaceStoredProcedure(spActiveEventFrameSummary, replaceWith = "d35f95abedc4.spActiveEventFrameSummary")
 