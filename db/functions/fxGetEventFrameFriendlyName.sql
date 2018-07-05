DELIMITER $$
DROP FUNCTION IF EXISTS fxGetEventFrameFriendlyName;
CREATE DEFINER=`pi`@`%` FUNCTION `fxGetEventFrameFriendlyName`(eventFrameId INT) RETURNS TEXT
BEGIN
	RETURN(SELECT IF(EventFrame.Name IS NOT NULL AND EventFrame.Name <> '', EventFrame.Name, CONCAT(DATE_FORMAT(EventFrame.StartTimestamp, '%m/%d/%y %H:%i'), ' - ', IF(EventFrame.EndTimestamp IS NULL, '', DATE_FORMAT(EventFrame.EndTimestamp, '%m/%d/%y %H:%i'))))
	FROM EventFrame
	WHERE EventFrame.EventFrameId = eventFrameId);
END$$
DELIMITER ;
