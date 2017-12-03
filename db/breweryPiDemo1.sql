-- MySQL dump 10.13  Distrib 5.7.20, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: brewerypidemo1
-- ------------------------------------------------------
-- Server version	5.7.20-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `area`
--

DROP TABLE IF EXISTS `area`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `area` (
  `AreaId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Abbreviation` varchar(10) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Name` varchar(45) NOT NULL,
  `SiteId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`AreaId`),
  UNIQUE KEY `AK_Area_Name_SiteId` (`Name`,`SiteId`),
  UNIQUE KEY `AK_Area_Abbreviation_SiteId` (`Abbreviation`,`SiteId`),
  KEY `FK__Site$Has$Area` (`SiteId`),
  CONSTRAINT `FK__Site$Has$Area` FOREIGN KEY (`SiteId`) REFERENCES `site` (`SiteId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `area`
--

LOCK TABLES `area` WRITE;
/*!40000 ALTER TABLE `area` DISABLE KEYS */;
INSERT INTO `area` VALUES (1,'C1','','Cellar 1',1);
/*!40000 ALTER TABLE `area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `attributetemplate`
--

DROP TABLE IF EXISTS `attributetemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `attributetemplate` (
  `AttributeTemplateId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Description` varchar(255) DEFAULT NULL,
  `ElementTemplateId` int(10) unsigned NOT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`AttributeTemplateId`),
  UNIQUE KEY `AK_AttributeTemplate_ElementTemplateId_Name` (`ElementTemplateId`,`Name`),
  KEY `FK__ElementTemplate$Has$AttributeTemplate` (`ElementTemplateId`),
  CONSTRAINT `FK__ElementTemplate$Has$AttributeTemplate` FOREIGN KEY (`ElementTemplateId`) REFERENCES `elementtemplate` (`ElementTemplateId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attributetemplate`
--

LOCK TABLES `attributetemplate` WRITE;
/*!40000 ALTER TABLE `attributetemplate` DISABLE KEYS */;
INSERT INTO `attributetemplate` VALUES (1,'',1,'Plato'),(2,'',1,'Temperature'),(3,'',1,'Pressure'),(4,'',1,'pH');
/*!40000 ALTER TABLE `attributetemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `element`
--

DROP TABLE IF EXISTS `element`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `element` (
  `ElementId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Description` varchar(255) DEFAULT NULL,
  `ElementTemplateId` int(10) unsigned NOT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`ElementId`),
  UNIQUE KEY `AK_Element_Name_ElementTemplateId` (`ElementTemplateId`,`Name`),
  KEY `FK__ElementTemplate$Has$Element` (`ElementTemplateId`),
  CONSTRAINT `FK__ElementTemplate$Has$Element` FOREIGN KEY (`ElementTemplateId`) REFERENCES `elementtemplate` (`ElementTemplateId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `element`
--

LOCK TABLES `element` WRITE;
/*!40000 ALTER TABLE `element` DISABLE KEYS */;
INSERT INTO `element` VALUES (1,'Fermentation Vessel 1',1,'FV01'),(2,'Fermentation Vessel 2',1,'FV02');
/*!40000 ALTER TABLE `element` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elementattribute`
--

DROP TABLE IF EXISTS `elementattribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `elementattribute` (
  `ElementAttributeId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `AttributeTemplateId` int(10) unsigned NOT NULL,
  `ElementId` int(10) unsigned NOT NULL,
  `TagId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`ElementAttributeId`),
  UNIQUE KEY `AK_ElementAttribute_AttributeTemplateId_ElementId` (`AttributeTemplateId`,`ElementId`),
  KEY `FK__AttributeTemplate$IsUsedIn$ElementAttribute` (`AttributeTemplateId`),
  KEY `FK__Element$IsUsedIn$ElementAttribute` (`ElementId`),
  KEY `FK__Tag$IsUsedIn$ElementAttribute` (`TagId`),
  CONSTRAINT `FK__AttributeTemplate$IsUsedIn$ElementAttribute` FOREIGN KEY (`AttributeTemplateId`) REFERENCES `attributetemplate` (`AttributeTemplateId`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK__Element$IsUsedIn$ElementAttribute` FOREIGN KEY (`ElementId`) REFERENCES `element` (`ElementId`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK__Tag$IsUsedIn$ElementAttribute` FOREIGN KEY (`TagId`) REFERENCES `tag` (`TagId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elementattribute`
--

LOCK TABLES `elementattribute` WRITE;
/*!40000 ALTER TABLE `elementattribute` DISABLE KEYS */;
INSERT INTO `elementattribute` VALUES (1,4,1,7),(2,1,1,1),(3,3,1,5),(4,2,1,3),(5,4,2,8),(6,1,2,2),(7,3,2,6),(8,2,2,4);
/*!40000 ALTER TABLE `elementattribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `elementtemplate`
--

DROP TABLE IF EXISTS `elementtemplate`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `elementtemplate` (
  `ElementTemplateId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Description` varchar(255) DEFAULT NULL,
  `Name` varchar(45) NOT NULL,
  `SiteId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`ElementTemplateId`),
  UNIQUE KEY `AK_ElementTemplate_Name_SiteId` (`SiteId`,`Name`),
  KEY `FK__Site$Has$ElementTemplate` (`SiteId`),
  CONSTRAINT `FK__Site$Has$ElementTemplate` FOREIGN KEY (`SiteId`) REFERENCES `site` (`SiteId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `elementtemplate`
--

LOCK TABLES `elementtemplate` WRITE;
/*!40000 ALTER TABLE `elementtemplate` DISABLE KEYS */;
INSERT INTO `elementtemplate` VALUES (1,'Fermentation Vessel','FV',1),(2,'Bright Beer Tank','BBT',1),(3,'Wort Kettle 1','WK1',1);
/*!40000 ALTER TABLE `elementtemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enterprise`
--

DROP TABLE IF EXISTS `enterprise`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `enterprise` (
  `EnterpriseId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Abbreviation` varchar(10) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`EnterpriseId`),
  UNIQUE KEY `AK_Enterprise_Name` (`Name`),
  UNIQUE KEY `AK_Enterprise_Abbreviation` (`Abbreviation`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enterprise`
--

LOCK TABLES `enterprise` WRITE;
/*!40000 ALTER TABLE `enterprise` DISABLE KEYS */;
INSERT INTO `enterprise` VALUES (1,'EP1','','Enterprise 1');
/*!40000 ALTER TABLE `enterprise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookup`
--

DROP TABLE IF EXISTS `lookup`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lookup` (
  `LookupId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `EnterpriseId` int(10) unsigned NOT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`LookupId`),
  UNIQUE KEY `AK_Lookup_EnterpriseId_Name` (`EnterpriseId`,`Name`),
  KEY `FK__Enterprise$Has$Lookup_idx` (`EnterpriseId`),
  CONSTRAINT `FK__Enterprise$Has$Lookup` FOREIGN KEY (`EnterpriseId`) REFERENCES `enterprise` (`EnterpriseId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookup`
--

LOCK TABLES `lookup` WRITE;
/*!40000 ALTER TABLE `lookup` DISABLE KEYS */;
/*!40000 ALTER TABLE `lookup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `lookupvalue`
--

DROP TABLE IF EXISTS `lookupvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `lookupvalue` (
  `LookupValueId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `LookupId` int(10) unsigned NOT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`LookupValueId`),
  UNIQUE KEY `AK_LookupValue_LookupId_Name` (`LookupId`,`Name`),
  KEY `FK__Lookup$Has$LookupValue_idx` (`LookupId`),
  CONSTRAINT `FK__Lookup$Has$LookupValue` FOREIGN KEY (`LookupId`) REFERENCES `lookup` (`LookupId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `lookupvalue`
--

LOCK TABLES `lookupvalue` WRITE;
/*!40000 ALTER TABLE `lookupvalue` DISABLE KEYS */;
/*!40000 ALTER TABLE `lookupvalue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `site`
--

DROP TABLE IF EXISTS `site`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `site` (
  `SiteId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Abbreviation` varchar(10) NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `EnterpriseId` int(10) unsigned NOT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`SiteId`),
  UNIQUE KEY `AK_Site_EnterpriseId_Name` (`EnterpriseId`,`Name`),
  UNIQUE KEY `AK_Site_Abbreviation_EnterpriseId` (`Abbreviation`,`EnterpriseId`),
  KEY `FK__Enterprise$Has$Site` (`EnterpriseId`),
  CONSTRAINT `FK__Enterprise$Has$Site` FOREIGN KEY (`EnterpriseId`) REFERENCES `enterprise` (`EnterpriseId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `site`
--

LOCK TABLES `site` WRITE;
/*!40000 ALTER TABLE `site` DISABLE KEYS */;
INSERT INTO `site` VALUES (1,'B1','',1,'Brewery 1');
/*!40000 ALTER TABLE `site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tag` (
  `TagId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `AreaId` int(10) unsigned NOT NULL,
  `Description` varchar(255) DEFAULT NULL,
  `LookupId` int(10) unsigned DEFAULT NULL,
  `Name` varchar(45) NOT NULL,
  `UnitOfMeasurementId` int(10) unsigned NOT NULL,
  PRIMARY KEY (`TagId`),
  UNIQUE KEY `AK_Tag_AreaId_Name` (`AreaId`,`Name`),
  KEY `FK__UnitOfMeasurement$IsUsedIn$Tag` (`UnitOfMeasurementId`),
  KEY `FK__Area$Has$Tag` (`AreaId`),
  KEY `FK__Lookup$$Tag_idx` (`LookupId`),
  CONSTRAINT `FK__Area$Has$Tag` FOREIGN KEY (`AreaId`) REFERENCES `area` (`AreaId`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK__Lookup$MayBeUsedIn$Tag` FOREIGN KEY (`LookupId`) REFERENCES `lookup` (`LookupId`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK__UnitOfMeasurement$IsUsedIn$Tag` FOREIGN KEY (`UnitOfMeasurementId`) REFERENCES `unitofmeasurement` (`UnitOfMeasurementId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tag`
--

LOCK TABLES `tag` WRITE;
/*!40000 ALTER TABLE `tag` DISABLE KEYS */;
INSERT INTO `tag` VALUES (1,1,'FV01 Plato',NULL,'FV01_Plato',4),(2,1,'FV02 Plato',NULL,'FV02_Plato',4),(3,1,'FV01 Temperature',NULL,'FV01_TIC001',2),(4,1,'FV02 Temperature',NULL,'FV02_TIC002',2),(5,1,'FV01 Pressure',NULL,'FV01_PIC001',41),(6,1,'FV02 Pressure',NULL,'FV02_PIC002',41),(7,1,'FV01 pH',NULL,'FV01_pH',27),(8,1,'FV02 pH',NULL,'FV02_pH',27),(9,1,'Total mass of yeast pitched',NULL,'FV01_PitchWeight',22),(10,1,'Total mass of yeast pitched',NULL,'FV02_PitchWeight',22),(11,1,'Tank full cell count',NULL,'FV01_TankFullCells',28);
/*!40000 ALTER TABLE `tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tagvalue`
--

DROP TABLE IF EXISTS `tagvalue`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tagvalue` (
  `TagValueId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `TagId` int(10) unsigned NOT NULL,
  `Timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Value` float NOT NULL,
  PRIMARY KEY (`TagValueId`),
  UNIQUE KEY `AK_TagValue_TagId_Timestamp` (`TagId`,`Timestamp`),
  KEY `FK__Tag$Has$Value` (`TagId`),
  CONSTRAINT `FK__Tag$Has$Value` FOREIGN KEY (`TagId`) REFERENCES `tag` (`TagId`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=156 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tagvalue`
--

LOCK TABLES `tagvalue` WRITE;
/*!40000 ALTER TABLE `tagvalue` DISABLE KEYS */;
INSERT INTO `tagvalue` VALUES (38,1,'2017-10-11 14:57:00',14.4),(39,1,'2017-10-12 02:20:00',11.5),(40,1,'2017-10-12 14:43:00',9.2),(41,1,'2017-10-13 02:13:00',7),(42,1,'2017-10-13 14:52:00',5.5),(43,1,'2017-10-14 03:01:00',4.8),(44,1,'2017-10-19 18:03:00',4.8),(45,1,'2017-10-25 14:12:00',14.4),(46,1,'2017-10-26 04:23:00',11.1),(47,1,'2017-10-26 14:20:00',9),(48,1,'2017-10-27 04:07:00',6.6),(49,1,'2017-10-27 14:47:00',5.7),(50,1,'2017-10-28 02:52:00',4.8),(51,1,'2017-10-28 16:37:00',4.6),(52,1,'2017-11-09 04:18:00',12.4),(53,1,'2017-11-09 15:48:00',10.3),(54,1,'2017-11-10 04:56:00',8.1),(55,1,'2017-11-10 15:54:00',6.3),(56,1,'2017-11-11 04:00:00',5),(57,1,'2017-11-28 15:55:00',15.5),(58,1,'2017-11-29 02:56:00',11.8),(59,1,'2017-11-29 14:57:00',9.1),(60,1,'2017-11-30 04:11:00',7),(61,1,'2017-11-30 15:49:00',5.3),(62,1,'2017-11-30 20:02:00',4.9),(63,2,'2017-10-02 13:56:00',13),(64,2,'2017-10-03 04:35:00',10.6),(65,2,'2017-10-03 14:44:00',8.1),(66,2,'2017-10-04 03:23:00',5.1),(67,2,'2017-10-04 14:11:00',3.8),(68,2,'2017-10-05 03:29:00',3.5),(69,2,'2017-10-16 03:06:00',13.7),(70,2,'2017-10-16 15:00:00',11.2),(71,2,'2017-10-17 03:23:00',9.1),(72,2,'2017-10-17 14:42:00',8.1),(73,2,'2017-10-18 03:11:00',6.8),(74,2,'2017-10-18 14:00:00',6.1),(75,2,'2017-10-19 03:50:00',5.6),(76,2,'2017-10-19 14:29:00',5.4),(77,2,'2017-10-19 23:54:00',5.3),(78,2,'2017-11-07 06:04:00',15.1),(79,2,'2017-11-07 15:15:00',12.7),(80,2,'2017-11-08 05:54:00',9.2),(81,2,'2017-11-08 15:40:00',7.3),(82,2,'2017-11-09 04:16:00',5.4),(83,2,'2017-11-09 12:50:00',4.7),(84,2,'2017-11-09 15:47:00',4.6),(85,2,'2017-11-22 05:28:00',12.3),(86,2,'2017-11-22 15:36:00',10.1),(87,2,'2017-11-23 04:54:00',7.7),(88,2,'2017-11-23 19:53:00',6.2),(89,2,'2017-11-24 18:14:00',4.8),(90,2,'2017-11-25 01:58:00',4.8),(91,2,'2017-11-25 17:33:00',4.6),(92,3,'2017-10-11 14:57:00',63),(93,3,'2017-10-12 02:20:00',63),(94,3,'2017-10-12 14:43:00',63),(95,3,'2017-10-13 02:13:00',62.9),(96,3,'2017-10-13 14:52:00',63.2),(97,3,'2017-10-14 03:01:00',64.2),(98,3,'2017-10-19 18:03:00',32),(99,3,'2017-10-25 14:12:00',62.9),(100,3,'2017-10-26 04:23:00',65),(101,3,'2017-10-26 14:20:00',63),(102,3,'2017-10-27 04:07:00',63),(103,3,'2017-10-27 14:47:00',63),(104,3,'2017-10-28 02:52:00',64),(105,3,'2017-10-28 16:37:00',64),(106,3,'2017-11-01 05:00:00',32),(107,3,'2017-11-09 04:18:00',63),(108,3,'2017-11-09 15:48:00',63.2),(109,3,'2017-11-10 04:56:00',62.9),(110,3,'2017-11-10 15:54:00',63.2),(111,3,'2017-11-11 04:00:00',64.3),(112,3,'2017-11-15 18:17:00',32),(113,3,'2017-11-28 15:55:00',63),(114,3,'2017-11-29 02:56:00',63),(115,3,'2017-11-29 14:57:00',63),(116,3,'2017-11-30 04:11:00',63),(117,3,'2017-11-30 15:49:00',65.4),(118,4,'2017-10-02 13:56:00',62),(119,4,'2017-10-03 04:35:00',63),(120,4,'2017-10-03 14:44:00',63),(121,4,'2017-10-04 03:23:00',63),(122,4,'2017-10-04 14:11:00',63.4),(123,4,'2017-10-05 03:29:00',64),(124,4,'2017-10-09 13:00:00',32),(125,4,'2017-10-16 03:06:00',63.1),(126,4,'2017-10-16 15:00:00',61.5),(127,4,'2017-10-17 03:23:00',63),(128,4,'2017-10-17 14:42:00',63),(129,4,'2017-10-18 03:11:00',64.6),(130,4,'2017-10-18 14:00:00',65.9),(131,4,'2017-10-19 03:50:00',66.9),(132,4,'2017-10-19 14:29:00',67.2),(133,4,'2017-10-23 20:41:00',32),(134,4,'2017-11-07 06:04:00',63.5),(135,4,'2017-11-07 15:15:00',65),(136,4,'2017-11-08 05:54:00',65),(137,4,'2017-11-08 15:40:00',65.3),(138,4,'2017-11-09 04:16:00',66.9),(139,4,'2017-11-09 12:50:00',67.8),(140,4,'2017-11-09 15:47:00',68.1),(141,4,'2017-11-15 05:06:00',32),(142,4,'2017-11-22 05:28:00',65),(143,4,'2017-11-22 15:36:00',65.1),(144,4,'2017-11-23 04:54:00',65),(145,4,'2017-11-23 19:53:00',67.2),(146,4,'2017-11-24 18:14:00',68),(147,4,'2017-11-25 01:58:00',67.8),(148,4,'2017-11-25 17:33:00',68),(149,4,'2017-11-29 21:30:00',32),(150,1,'2017-12-01 21:11:21',16.7);
/*!40000 ALTER TABLE `tagvalue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `unitofmeasurement`
--

DROP TABLE IF EXISTS `unitofmeasurement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `unitofmeasurement` (
  `UnitOfMeasurementId` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `Abbreviation` varchar(15) NOT NULL,
  `Name` varchar(45) NOT NULL,
  PRIMARY KEY (`UnitOfMeasurementId`),
  UNIQUE KEY `AK_UnitOfMeasurement_Abbreviation_Name` (`Abbreviation`,`Name`)
) ENGINE=InnoDB AUTO_INCREMENT=44 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `unitofmeasurement`
--

LOCK TABLES `unitofmeasurement` WRITE;
/*!40000 ALTER TABLE `unitofmeasurement` DISABLE KEYS */;
INSERT INTO `unitofmeasurement` VALUES (23,'#','number'),(9,'%','percent'),(19,': 1','ratio'),(31,'abv','alcohol by volume'),(6,'ADF','apparent degree of fermentation'),(11,'ae','ae'),(34,'ASBC','American Society of Brewing Chemists'),(1,'bbl','barrel'),(33,'cells/ml','cells per milliliter'),(36,'cells/ml/°P','cells per ml per °P'),(29,'EBC','european brewery convention'),(21,'g','grams'),(40,'g/bbl','grams per barrel'),(42,'g/L','grams per liter'),(25,'gal','gallon'),(17,'gpm','gallons per minute'),(15,'h','hour'),(7,'IBU','international bittering unit'),(26,'in','inches'),(38,'kg','kilogram'),(22,'lb','pound'),(32,'lb/bbl','pounds / barrel'),(37,'mg','milligram'),(13,'min','minute'),(39,'mL','milliliter'),(16,'mm','millimeter'),(27,'pH','potential of hydrogen'),(30,'ppb','parts per billion'),(10,'ppm','parts per million'),(41,'psi','pounds per square inch'),(8,'RE','real extract'),(14,'s','second'),(5,'SG','specific gravity'),(43,'SRM','Standard Reference Method'),(18,'t/h','tons per hour'),(35,'vol','volumes'),(24,'x10^12 cells','x10^12 cells'),(28,'x10^6 cells','x10^6 cells'),(3,'°C','degree Celsius'),(2,'°F','degree Fahrenheit'),(20,'°F/min','degree Fahrenheit per minute'),(12,'°L','degree Lovibond'),(4,'°P','plato');
/*!40000 ALTER TABLE `unitofmeasurement` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-12-02 15:54:24
