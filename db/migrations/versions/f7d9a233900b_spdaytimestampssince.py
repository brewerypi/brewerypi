"""spDayTimestampsSince

Revision ID: f7d9a233900b
Revises: fa707933be8d
Create Date: 2019-05-27 23:25:45.661486

"""
from alembic import op
import sqlalchemy as sa
from db.migrations.replaceableObjects import ReplaceableObject


# revision identifiers, used by Alembic.
revision = 'f7d9a233900b'
down_revision = 'fa707933be8d'
branch_labels = None
depends_on = None


spDayTimestampsSince = ReplaceableObject(
    "spDayTimestampsSince",
    "IN since DATETIME",
    None,
    """
BEGIN
	SET @numberOfDaysBetween = NULL;
	SET @sql = NULL;

	SELECT DATEDIFF(NOW(), since) INTO @numberOfDaysBetween;
	SET @sql = CONCAT('SELECT UNIX_TIMESTAMP(''', since, ''' + INTERVAL (seq) DAY) AS time_sec, CONCAT(''Day '', (seq)) AS text, CONCAT(''Day '', (seq)) as tags FROM seq_1_to_', @numberOfDaysBetween);

	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END""")


def upgrade():
    op.createStoredProcedure(spDayTimestampsSince)

def downgrade():
    op.dropStoredProcedure(spDayTimestampsSince)
