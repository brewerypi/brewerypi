"""empty message

Revision ID: d35f95abedc4
Revises: ef09d330ca05
Create Date: 2018-11-25 17:24:38.052757

"""
from alembic import op
from flask import current_app
import sqlalchemy as sa
from sqlalchemy import func
from sqlalchemy.dialects import mysql
from pytz import exceptions, timezone
import pytz
from app import db
from app.models import EventFrame, Note, TagValue
from db.migrations.replaceableObjects import ReplaceableObject
from db.migrations.versions.f64c7735ec58_ import fxGetEventFrameFriendlyName


# revision identifiers, used by Alembic.
revision = 'd35f95abedc4'
down_revision = 'ef09d330ca05'
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
            t1.Name,
			Element.Name AS Element,
			t1.StartTimestamp AS Start,
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
			EventFrameTemplate.EventFrameTemplateId IN (', eventFrameTemplateIds ,') AND
            (t3.Timestamp >= t1.StartTimestamp OR t3.Value IS NULL)
        GROUP BY t1.EventFrameId
		UNION ALL
		SELECT EventFrameTemplate.Name AS Template,
            EventFrame.Name,
			Element.Name AS Element,
			EventFrame.StartTimestamp AS Start,
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
END""")


def convertLocalToUtc():
    eventFrames = EventFrame.query.all()
    notes = Note.query.all()
    tagValues = TagValue.query.all()
    if len(eventFrames) > 0 or len(notes) > 0 or len(tagValues) > 0:
        localTimezone = timezone(current_app.config["LOCAL_TIMEZONE"])
        utcTimezone = timezone("UTC")
        for eventFrame in eventFrames:
            try:
                localTimezone.utcoffset(eventFrame.StartTimestamp)
            except pytz.exceptions.AmbiguousTimeError:
                print("Event Frame Id: {} has an ambiguous start timestamp and should be verified.".format(eventFrame.EventFrameId))

            localStartTimestamp = localTimezone.localize(eventFrame.StartTimestamp)
            eventFrame.StartTimestamp = localStartTimestamp.astimezone(utcTimezone)

            if eventFrame.EndTimestamp is not None:
                try:
                    localTimezone.utcoffset(eventFrame.EndTimestamp)
                except pytz.exceptions.AmbiguousTimeError:
                    print("Event Frame Id: {} has an ambiguous end timestamp and should be verified.".format(eventFrame.EventFrameId))

                localEndTimestamp = localTimezone.localize(eventFrame.EndTimestamp)
                eventFrame.EndTimestamp = localEndTimestamp.astimezone(utcTimezone)

        for note in notes:
            try:
                localTimezone.utcoffset(note.Timestamp)
            except pytz.exceptions.AmbiguousTimeError:
                print("Note Id: {} has an ambiguous timestamp and should be verified.".format(note.NoteId))

            localTimestamp = localTimezone.localize(note.Timestamp)
            note.Timestamp = localTimestamp.astimezone(utcTimezone)

        for tagValue in tagValues:
            try:
                localTimezone.utcoffset(tagValue.Timestamp)
            except pytz.exceptions.AmbiguousTimeError:
                print("Tag Value Id: {} has an ambiguous timestamp and should be verified.".format(tagValue.TagValueId))

            localTimestamp = localTimezone.localize(tagValue.Timestamp)
            tagValue.Timestamp = localTimestamp.astimezone(utcTimezone)

        db.session.commit()

def convertUtcToLocal():
    eventFrames = EventFrame.query.all()
    notes = Note.query.all()
    tagValues = TagValue.query.all()
    if len(eventFrames) > 0 or len(notes) > 0 or len(tagValues) > 0:
        localTimezone = timezone(current_app.config["LOCAL_TIMEZONE"])
        utcTimezone = timezone("UTC")
        for eventFrame in eventFrames:
            utcStartTimestamp = utcTimezone.localize(eventFrame.StartTimestamp)
            eventFrame.StartTimestamp = utcStartTimestamp.astimezone(localTimezone)
            if eventFrame.EndTimestamp is not None:
                utcEndTimestamp = utcTimezone.localize(eventFrame.EndTimestamp)
                eventFrame.EndTimestamp = utcEndTimestamp.astimezone(localTimezone)

        for note in notes:
            utcTimestamp = utcTimezone.localize(note.Timestamp)
            note.Timestamp = utcTimestamp.astimezone(localTimezone)

        for tagValue in tagValues:
            utcTimestamp = utcTimezone.localize(tagValue.Timestamp)
            tagValue.Timestamp = utcTimestamp.astimezone(localTimezone)

        db.session.commit()

def setNullEventFrameNames():
    eventFrames = EventFrame.query.all()
    for eventFrame in eventFrames:
        if eventFrame.Name is None or eventFrame.Name == "":
            print("Setting Event Frame Id: {} name to unix timestamp based on start timestamp.".format(eventFrame.EventFrameId))
            eventFrame.Name = func.unix_timestamp(eventFrame.StartTimestamp)

    db.session.commit()

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('FK__ElementAttributeTemplate$Have$ElementAttribute', 'ElementAttribute', type_='foreignkey')
    op.alter_column('ElementAttribute', 'ElementAttributeTemplateId',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=False)
    op.create_foreign_key('FK__ElementAttributeTemplate$Have$ElementAttribute', 'ElementAttribute', 'ElementAttributeTemplate', ['ElementAttributeTemplateId'], ['ElementAttributeTemplateId'])
    setNullEventFrameNames()
    op.alter_column('EventFrame', 'Name',
               existing_type=mysql.VARCHAR(length=45),
               nullable=False)
    op.create_index('IX__StartTimestamp__EndTimestamp', 'EventFrame', ['StartTimestamp', 'EndTimestamp'], unique=False)
    op.dropFunction(fxGetEventFrameFriendlyName)
    convertLocalToUtc()
    op.replaceStoredProcedure(spActiveEventFrameSummary, replaces = "ef09d330ca05.spActiveEventFrameSummary")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.createFunction(fxGetEventFrameFriendlyName)
    op.drop_index('IX__StartTimestamp__EndTimestamp', table_name='EventFrame')
    op.alter_column('EventFrame', 'Name',
               existing_type=mysql.VARCHAR(length=45),
               nullable=True)
    op.alter_column('ElementAttribute', 'ElementAttributeTemplateId',
               existing_type=mysql.INTEGER(display_width=11),
               nullable=True)
    convertUtcToLocal()
    op.replaceStoredProcedure(spActiveEventFrameSummary, replaceWith = "ef09d330ca05.spActiveEventFrameSummary")
    # ### end Alembic commands ###
