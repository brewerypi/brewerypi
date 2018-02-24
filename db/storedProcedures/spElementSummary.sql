DELIMITER $$
CREATE DEFINER=`pi`@`%` PROCEDURE `spElementSummary`(IN attributeTemplateIds TEXT, IN elementIds TEXT)
BEGIN
	SET @@group_concat_max_len = 5000;
	SET @sql = NULL;

	SELECT GROUP_CONCAT(DISTINCT CONCAT('MAX(IF(AttributeTemplate.Name = ''', AttributeTemplate.Name, ''', IF(Tag.LookupId IS NULL, t3.Value, LookupValue.Name), '''')) AS ''', AttributeTemplate.Name, '''')) INTO @sql
	FROM AttributeTemplate
    WHERE AttributeTemplate.ElementTemplateId = elementTemplateId AND
		FIND_IN_SET(AttributeTemplate.AttributeTemplateId, attributeTemplateIds) > 0;

	SET @sql = CONCAT('SELECT t2.Name AS ''Element'', ElementTemplate.Name AS ''Template'', ', @sql, ' FROM ElementAttribute t1 INNER JOIN AttributeTemplate ON t1.AttributeTemplateId = AttributeTemplate.AttributeTemplateId INNER JOIN Element t2 ON t1.ElementId = t2.ElementId INNER JOIN ElementTemplate ON t2.ElementTemplateId = ElementTemplate.ElementTemplateId INNER JOIN Tag ON t1.TagId = Tag.TagId LEFT OUTER JOIN Lookup ON Tag.LookupId = Lookup.LookupId LEFT OUTER JOIN LookupValue ON Lookup.LookupId = LookupValue.LookupId INNER JOIN TagValue t3 ON CASE WHEN Tag.LookupId IS NULL THEN Tag.TagId = t3.TagId ELSE Tag.TagId = t3.TagId AND LookupValue.Value = t3.Value END INNER JOIN (SELECT ElementAttribute.ElementId, AttributeTemplate.AttributeTemplateId, MAX(TagValue.Timestamp) AS MaxTimestamp FROM ElementAttribute INNER JOIN AttributeTemplate ON ElementAttribute.AttributeTemplateId = AttributeTemplate.AttributeTemplateId INNER JOIN Tag ON ElementAttribute.TagId = Tag.TagId INNER JOIN TagValue ON Tag.TagId = TagValue.TagId GROUP BY ElementAttribute.ElementId, AttributeTemplate.AttributeTemplateId) t4 ON t1.ElementId = t4.ElementId AND t1.AttributeTemplateId = t4.AttributeTemplateId AND t3.Timestamp = t4.MaxTimestamp WHERE t2.ElementId IN (', elementIds ,') GROUP BY t1.ElementId ORDER BY ElementTemplate.Name, t2.Name');

	PREPARE stmt FROM @sql;
	EXECUTE stmt;
	DEALLOCATE PREPARE stmt;
END$$
DELIMITER ;
