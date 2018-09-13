"""empty message

Revision ID: ef09d330ca05
Revises: f64c7735ec58
Create Date: 2018-06-16 09:32:46.708758

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from app.replaceableObjects import ReplaceableObject


# revision identifiers, used by Alembic.
revision = 'ef09d330ca05'
down_revision = 'f64c7735ec58'
branch_labels = None
depends_on = None


spElementSummary = ReplaceableObject(
    "spElementSummary",
    "IN elementAttributeTemplateNames TEXT, IN elementIds TEXT",
    None,
    """
BEGIN
	SET @@group_concat_max_len = 5000;
	SET @sql = NULL;

	SELECT GROUP_CONCAT(DISTINCT CONCAT('MAX(IF(ElementAttributeTemplate.Name = ''', ElementAttributeTemplate.Name, ''', IF(Tag.LookupId IS NULL, t3.Value, LookupValue.Name), '''')) AS ''', ElementAttributeTemplate.Name, '''')) INTO @sql
	FROM ElementAttributeTemplate
    WHERE FIND_IN_SET(ElementAttributeTemplate.Name, elementAttributeTemplateNames) > 0;

	SET @sql = CONCAT('SELECT t2.Name AS ''Element'', ElementTemplate.Name AS ''Template'', ', @sql, ' FROM ElementAttribute t1 INNER JOIN ElementAttributeTemplate ON t1.ElementAttributeTemplateId = ElementAttributeTemplate.ElementAttributeTemplateId INNER JOIN Element t2 ON t1.ElementId = t2.ElementId INNER JOIN ElementTemplate ON t2.ElementTemplateId = ElementTemplate.ElementTemplateId INNER JOIN Tag ON t1.TagId = Tag.TagId LEFT OUTER JOIN Lookup ON Tag.LookupId = Lookup.LookupId LEFT OUTER JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId INNER JOIN TagValue t3 ON CASE WHEN Tag.LookupId IS NULL THEN Tag.TagId = t3.TagId ELSE Tag.TagId = t3.TagId AND LookupValue.Value = t3.Value END INNER JOIN (SELECT ElementAttribute.ElementId, ElementAttributeTemplate.ElementAttributeTemplateId, MAX(TagValue.Timestamp) AS MaxTimestamp FROM ElementAttribute INNER JOIN ElementAttributeTemplate ON ElementAttribute.ElementAttributeTemplateId = ElementAttributeTemplate.ElementAttributeTemplateId INNER JOIN Tag ON ElementAttribute.TagId = Tag.TagId INNER JOIN TagValue ON Tag.TagId = TagValue.TagId GROUP BY ElementAttribute.ElementId, ElementAttributeTemplate.ElementAttributeTemplateId) t4 ON t1.ElementId = t4.ElementId AND t1.ElementAttributeTemplateId = t4.ElementAttributeTemplateId AND t3.Timestamp = t4.MaxTimestamp WHERE t2.ElementId IN (', elementIds ,') GROUP BY t1.ElementId ORDER BY ElementTemplate.Name, t2.Name');

	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END;
    """
)


spActiveEventFrameSummary = ReplaceableObject(
    "spActiveEventFrameSummary",
    "IN eventFrameTemplateIds TEXT, IN eventFrameAttributeTemplateNames TEXT",
    None,
    """
BEGIN
	SET @@group_concat_max_len = 5000;
	SET @sql = NULL;
	SET @query1DynamicColumns = NULL;
	SET @query2DynamicColumns = NULL;

	SELECT GROUP_CONCAT(DISTINCT CONCAT('MAX(IF(t2.Name = ''', EventFrameAttributeTemplate.Name, ''', IF(Tag.LookupId IS NULL, t3.Value, LookupValue.Name), '''')) AS ''', EventFrameAttributeTemplate.Name, '''')) INTO @query1DynamicColumns
	FROM EventFrameAttributeTemplate
    WHERE FIND_IN_SET(EventFrameAttributeTemplate.Name, eventFrameAttributeTemplateNames) > 0;

	SELECT GROUP_CONCAT(DISTINCT CONCAT('NULL AS ''', EventFrameAttributeTemplate.Name, '''')) INTO @query2DynamicColumns
	FROM EventFrameAttributeTemplate
    WHERE FIND_IN_SET(EventFrameAttributeTemplate.Name, eventFrameAttributeTemplateNames) > 0;

	SET @sql = CONCAT('
		SELECT EventFrameTemplate.Name  AS Template,
			Element.Name AS Element,
			DATE_FORMAT(t1.StartTimestamp, ''%m/%d/%y %H:%i'') AS Start,
            ', @query1DynamicColumns, '
		FROM EventFrame t1
			INNER JOIN EventFrameTemplate ON t1.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
            INNER JOIN EventFrameAttributeTemplate t2 ON EventFrameTemplate.EventFrameTemplateId = t2.EventFrameTemplateId
            INNER JOIN EventFrameAttribute ON t2.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId
            INNER JOIN Element ON t1.ElementId = Element.ElementId AND EventFrameAttribute.ElementId = Element.ElementId
            INNER JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
            LEFT JOIN Lookup ON Tag.LookupId = Lookup.LookupId
            LEFT JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId
            INNER JOIN TagValue t3 ON
				CASE
					WHEN Tag.LookupId IS NULL
						THEN Tag.TagId = t3.TagId
					ELSE
						Tag.TagId = t3.TagId AND LookupValue.Value = t3.Value
				END
			INNER JOIN
            (
				SELECT EventFrame.EventFrameId,
					EventFrameAttributeTemplate.Name,
                    Max(TagValue.Timestamp) AS MaxTimestamp
				FROM EventFrame
					INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
                    INNER JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
                    INNER JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId
                    INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
						AND EventFrameAttribute.ElementId = Element.ElementId
					INNER JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
                    INNER JOIN TagValue ON Tag.TagId = TagValue.TagId
				WHERE EventFrame.EndTimestamp IS NULL AND
					EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds ,')
                GROUP BY EventFrame.EventFrameId,
					EventFrameAttributeTemplate.Name
			) t4 ON t1.EventFrameId = t4.EventFrameId AND
				t2.Name = t4.Name AND
				t3.Timestamp = t4.MaxTimestamp
		WHERE t1.EndTimestamp IS NULL AND
			EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds ,')
        GROUP BY t1.EventFrameId
		UNION ALL
		SELECT EventFrameTemplate.Name AS Template,
			Element.Name AS Element,
			DATE_FORMAT(EventFrame.StartTimestamp, ''%m/%d/%y %H:%i'') AS Start,
            ', @query2DynamicColumns, '
		FROM EventFrame
			INNER JOIN Element ON EventFrame.ElementId = Element.ElementId
			INNER JOIN EventFrameTemplate ON EventFrame.EventFrameTemplateId = EventFrameTemplate.EventFrameTemplateId
			INNER JOIN EventFrameAttributeTemplate ON EventFrameTemplate.EventFrameTemplateId = EventFrameAttributeTemplate.EventFrameTemplateId
			LEFT JOIN EventFrameAttribute ON EventFrameAttributeTemplate.EventFrameAttributeTemplateId = EventFrameAttribute.EventFrameAttributeTemplateId AND
				Element.ElementId = EventFrameAttribute.ElementId
			LEFT JOIN Tag ON EventFrameAttribute.TagId = Tag.TagId
			LEFT JOIN TagValue ON Tag.TagId = TagValue.TagId
		WHERE EventFrame.EndTimestamp IS NULL AND
			EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds ,') AND
			(TagValue.Timestamp >= EventFrame.StartTimestamp OR TagValue.Value IS NULL)
		GROUP BY EventFrame.EventFrameId
		HAVING (COUNT(TagValue.Value) = 0)
		ORDER BY Template,
			Element');

	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END;
    """
)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ElementAttributeTemplate',
    sa.Column('ElementAttributeTemplateId', sa.Integer(), nullable=False),
    sa.Column('Description', sa.String(length=255), nullable=True),
    sa.Column('ElementTemplateId', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(length=45), nullable=False),
    sa.ForeignKeyConstraint(['ElementTemplateId'], ['ElementTemplate.ElementTemplateId'], name='FK__ElementTemplate$Have$ElementAttributeTemplate'),
    sa.PrimaryKeyConstraint('ElementAttributeTemplateId'),
    sa.UniqueConstraint('ElementTemplateId', 'Name', name='AK__ElementTemplateId__Name')
    )

    # Insert AttributeTemplate records into ElementAttributeTemplate table.
    metadata = sa.MetaData()
    metadata.reflect(bind = op.get_bind())
    attributeTemplates = metadata.tables["AttributeTemplate"]
    elementAttributeTemplates = metadata.tables["ElementAttributeTemplate"]
    selectStatement = sa.select([attributeTemplates])
    resultProxy = op.get_bind().execute(selectStatement)
    for record in resultProxy:
        insertStatement = elementAttributeTemplates.insert().values(ElementAttributeTemplateId = record.AttributeTemplateId, Description = record.Description,
            ElementTemplateId = record.ElementTemplateId, Name = record.Name)
        op.get_bind().execute(insertStatement)

    op.create_table('EventFrameAttributeTemplate',
    sa.Column('EventFrameAttributeTemplateId', sa.Integer(), nullable=False),
    sa.Column('Description', sa.String(length=255), nullable=True),
    sa.Column('EventFrameTemplateId', sa.Integer(), nullable=False),
    sa.Column('Name', sa.String(length=45), nullable=False),
    sa.ForeignKeyConstraint(['EventFrameTemplateId'], ['EventFrameTemplate.EventFrameTemplateId'], name='FK__EventFrameTemplate$Have$EventFrameAttributeTemplate'),
    sa.PrimaryKeyConstraint('EventFrameAttributeTemplateId'),
    sa.UniqueConstraint('EventFrameTemplateId', 'Name', name='AK__EventFrameTemplateId__Name')
    )
    op.create_table('EventFrameAttribute',
    sa.Column('EventFrameAttributeId', sa.Integer(), nullable=False),
    sa.Column('ElementId', sa.Integer(), nullable=False),
    sa.Column('EventFrameAttributeTemplateId', sa.Integer(), nullable=False),
    sa.Column('TagId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['ElementId'], ['Element.ElementId'], name='FK__Element$Have$EventFrameAttribute'),
    sa.ForeignKeyConstraint(['EventFrameAttributeTemplateId'], ['EventFrameAttributeTemplate.EventFrameAttributeTemplateId'], name='FK__EventFrameAttributeTemplate$Have$EventFrameAttribute'),
    sa.ForeignKeyConstraint(['TagId'], ['Tag.TagId'], name='FK__Tag$Have$EventFrameAttribute'),
    sa.PrimaryKeyConstraint('EventFrameAttributeId'),
    sa.UniqueConstraint('EventFrameAttributeTemplateId', 'ElementId', name='AK__EventFrameAttributeTemplateId__ElementId')
    )
    # Added dropping of constraint FK__ElementTemplate$Have$AttributeTemplate prior to being allowed to drop index AK__ElementTemplateId__Name.
    op.drop_constraint('FK__ElementTemplate$Have$AttributeTemplate', 'AttributeTemplate', type_='foreignkey')
    op.drop_index('AK__ElementTemplateId__Name', table_name='AttributeTemplate')
    # Moved this up so that dropping of table AttributeTemplate does not fail.
    op.drop_constraint('FK__AttributeTemplate$Have$ElementAttribute', 'ElementAttribute', type_='foreignkey')
    op.drop_table('AttributeTemplate')
    op.add_column('ElementAttribute', sa.Column('ElementAttributeTemplateId', sa.Integer(), nullable=False))

    # Update ElementAttributeTemplateId to AttributeTemplateId in ElementAttribute table.
    metadata2 = sa.MetaData()
    metadata2.reflect(bind = op.get_bind())
    elementAttributes = metadata2.tables["ElementAttribute"]
    updateStatement = elementAttributes.update().values(ElementAttributeTemplateId = elementAttributes.c.AttributeTemplateId)
    op.get_bind().execute(updateStatement)
    op.get_bind().execute("ALTER TABLE ElementAttribute MODIFY ElementAttributeTemplateId INT(11) AFTER ElementAttributeId")

    op.create_unique_constraint('AK__ElementAttributeTemplateId__ElementId', 'ElementAttribute', ['ElementAttributeTemplateId', 'ElementId'])
    op.drop_index('AK__AttributeTemplateId__ElementId', table_name='ElementAttribute')
    # op.drop_constraint('FK__AttributeTemplate$Have$ElementAttribute', 'ElementAttribute', type_='foreignkey')
    op.create_foreign_key('FK__ElementAttributeTemplate$Have$ElementAttribute', 'ElementAttribute', 'ElementAttributeTemplate', ['ElementAttributeTemplateId'], ['ElementAttributeTemplateId'])
    op.drop_column('ElementAttribute', 'AttributeTemplateId')
    op.createStoredProcedure(spActiveEventFrameSummary)
    op.replaceStoredProcedure(spElementSummary, replaces = "1476a62140ae.spElementSummary")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.dropStoredProcedure(spActiveEventFrameSummary)
    op.add_column('ElementAttribute', sa.Column('AttributeTemplateId', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False))
    op.drop_constraint('FK__ElementAttributeTemplate$Have$ElementAttribute', 'ElementAttribute', type_='foreignkey')
    # op.create_foreign_key('FK__AttributeTemplate$Have$ElementAttribute', 'ElementAttribute', 'AttributeTemplate', ['AttributeTemplateId'], ['AttributeTemplateId'])

    # Update AttributeTemplateId to ElementAttributeTemplateId in ElementAttribute table.
    metadata = sa.MetaData()
    metadata.reflect(bind = op.get_bind())
    elementAttributes = metadata.tables["ElementAttribute"]
    updateStatement = elementAttributes.update().values(AttributeTemplateId = elementAttributes.c.ElementAttributeTemplateId)
    op.get_bind().execute(updateStatement)
    op.get_bind().execute("ALTER TABLE ElementAttribute MODIFY AttributeTemplateId INT(11) AFTER ElementAttributeId")

    op.create_index('AK__AttributeTemplateId__ElementId', 'ElementAttribute', ['AttributeTemplateId', 'ElementId'], unique=True)
    op.drop_constraint('AK__ElementAttributeTemplateId__ElementId', 'ElementAttribute', type_='unique')
    op.drop_column('ElementAttribute', 'ElementAttributeTemplateId')
    op.create_table('AttributeTemplate',
    sa.Column('AttributeTemplateId', mysql.INTEGER(display_width=11), nullable=False),
    sa.Column('Description', mysql.VARCHAR(length=255), nullable=True),
    sa.Column('ElementTemplateId', mysql.INTEGER(display_width=11), autoincrement=False, nullable=False),
    sa.Column('Name', mysql.VARCHAR(length=45), nullable=False),
    sa.ForeignKeyConstraint(['ElementTemplateId'], ['ElementTemplate.ElementTemplateId'], name='FK__ElementTemplate$Have$AttributeTemplate'),
    sa.PrimaryKeyConstraint('AttributeTemplateId'),
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )

    # Insert ElementAttributeTemplate records into AttributeTemplate table.
    metadata2 = sa.MetaData()
    metadata2.reflect(bind = op.get_bind())
    attributeTemplates = metadata2.tables["AttributeTemplate"]
    elementAttributeTemplates = metadata2.tables["ElementAttributeTemplate"]
    selectStatement = sa.select([elementAttributeTemplates])
    resultProxy = op.get_bind().execute(selectStatement)
    for record in resultProxy:
        insertStatement = attributeTemplates.insert().values(AttributeTemplateId = record.ElementAttributeTemplateId, Description = record.Description,
            ElementTemplateId = record.ElementTemplateId, Name = record.Name)
        op.get_bind().execute(insertStatement)

    # Moved this down after the AttributeTemplate table is created.
    op.create_foreign_key('FK__AttributeTemplate$Have$ElementAttribute', 'ElementAttribute', 'AttributeTemplate', ['AttributeTemplateId'], ['AttributeTemplateId'])
    op.create_index('AK__ElementTemplateId__Name', 'AttributeTemplate', ['ElementTemplateId', 'Name'], unique=True)
    op.drop_table('EventFrameAttribute')
    op.drop_table('EventFrameAttributeTemplate')
    op.drop_table('ElementAttributeTemplate')
    op.replaceStoredProcedure(spElementSummary, replaceWith = "1476a62140ae.spElementSummary")
    # ### end Alembic commands ###
