"""empty message

Revision ID: 52534bd6783e
Revises: 4d3c54f0e71b
Create Date: 2019-02-23 09:56:08.668352

"""
from alembic import op
import sqlalchemy as sa
from db.migrations.replaceableObjects import ReplaceableObject
# Can't use from x import y if y  starts with a number.
# from db.migrations.versions.4d3c54f0e71b_ import spCurrentEventFrameAttributeValues
from importlib import import_module
spCurrentEventFrameAttributeValues = import_module("db.migrations.versions.4d3c54f0e71b_").spCurrentEventFrameAttributeValues


# revision identifiers, used by Alembic.
revision = '52534bd6783e'
down_revision = '4d3c54f0e71b'
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
				WHERE EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds, ') AND
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
		WHERE EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds, ') AND
			EventFrame.EndTimestamp IS NULL
		GROUP BY EventFrame.EventFrameId
        ORDER BY Template, Element');

	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END""")


def upgrade():
	op.dropStoredProcedure(spCurrentEventFrameAttributeValues)
	op.replaceStoredProcedure(spActiveEventFrameSummary, replaces = "4d3c54f0e71b.spActiveEventFrameSummary")


def downgrade():
	op.createStoredProcedure(spCurrentEventFrameAttributeValues)
	op.replaceStoredProcedure(spActiveEventFrameSummary, replaceWith = "4d3c54f0e71b.spActiveEventFrameSummary")
