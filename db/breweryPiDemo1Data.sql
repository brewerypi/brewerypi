-- MySQL dump 10.13  Distrib 5.7.20, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: BreweryPiDemo1
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
-- Dumping data for table `Area`
--

LOCK TABLES `Area` WRITE;
/*!40000 ALTER TABLE `Area` DISABLE KEYS */;
INSERT INTO `Area` VALUES (1,'C1','','Cellar 1',1),(2,'BH1','','Brewhouse 1',1);
/*!40000 ALTER TABLE `Area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `AttributeTemplate`
--

LOCK TABLES `AttributeTemplate` WRITE;
/*!40000 ALTER TABLE `AttributeTemplate` DISABLE KEYS */;
INSERT INTO `AttributeTemplate` VALUES (1,'',1,'Plato'),(2,'',1,'Temperature'),(3,'',1,'Pressure'),(4,'',1,'pH');
/*!40000 ALTER TABLE `AttributeTemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Element`
--

LOCK TABLES `Element` WRITE;
/*!40000 ALTER TABLE `Element` DISABLE KEYS */;
INSERT INTO `Element` VALUES (1,'Fermentation Vessel 1',1,'FV01'),(2,'Fermentation Vessel 2',1,'FV02');
/*!40000 ALTER TABLE `Element` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `ElementAttribute`
--

LOCK TABLES `ElementAttribute` WRITE;
/*!40000 ALTER TABLE `ElementAttribute` DISABLE KEYS */;
INSERT INTO `ElementAttribute` VALUES (1,4,1,7),(2,1,1,1),(3,3,1,5),(4,2,1,3),(5,4,2,8),(6,1,2,2),(7,3,2,6),(8,2,2,4);
/*!40000 ALTER TABLE `ElementAttribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `ElementTemplate`
--

LOCK TABLES `ElementTemplate` WRITE;
/*!40000 ALTER TABLE `ElementTemplate` DISABLE KEYS */;
INSERT INTO `ElementTemplate` VALUES (1,'Fermentation Vessel','FV',1),(2,'Bright Beer Tank','BBT',1),(3,'Wort Kettle 1','WK1',1);
/*!40000 ALTER TABLE `ElementTemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Enterprise`
--

LOCK TABLES `Enterprise` WRITE;
/*!40000 ALTER TABLE `Enterprise` DISABLE KEYS */;
INSERT INTO `Enterprise` VALUES (1,'EP1','','Enterprise 1');
/*!40000 ALTER TABLE `Enterprise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Lookup`
--

LOCK TABLES `Lookup` WRITE;
/*!40000 ALTER TABLE `Lookup` DISABLE KEYS */;
INSERT INTO `Lookup` VALUES (2,1,'Brands'),(3,1,'Status');
/*!40000 ALTER TABLE `Lookup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `LookupValue`
--

LOCK TABLES `LookupValue` WRITE;
/*!40000 ALTER TABLE `LookupValue` DISABLE KEYS */;
/*!40000 ALTER TABLE `LookupValue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Site`
--

LOCK TABLES `Site` WRITE;
/*!40000 ALTER TABLE `Site` DISABLE KEYS */;
INSERT INTO `Site` VALUES (1,'B1','',1,'Brewery 1');
/*!40000 ALTER TABLE `Site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Tag`
--

LOCK TABLES `Tag` WRITE;
/*!40000 ALTER TABLE `Tag` DISABLE KEYS */;
INSERT INTO `Tag` VALUES (1,1,'FV01 Plato',NULL,'FV01_Plato',4),(2,1,'FV02 Plato',NULL,'FV02_Plato',4),(3,1,'FV01 Temperature',NULL,'FV01_TIC001',2),(4,1,'FV02 Temperature',NULL,'FV02_TIC002',2),(5,1,'FV01 Pressure',NULL,'FV01_PIC001',41),(6,1,'FV02 Pressure',NULL,'FV02_PIC002',41),(7,1,'FV01 pH',NULL,'FV01_pH',27),(8,1,'FV02 pH',NULL,'FV02_pH',27),(9,1,'Total mass of yeast pitched',NULL,'FV01_PitchWeight',22),(10,1,'Total mass of yeast pitched',NULL,'FV02_PitchWeight',22),(11,1,'Tank full cell count',NULL,'FV01_TankFullCells',28);
/*!40000 ALTER TABLE `Tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `TagValue`
--

LOCK TABLES `TagValue` WRITE;
/*!40000 ALTER TABLE `TagValue` DISABLE KEYS */;
INSERT INTO `TagValue` VALUES (38,1,'2017-10-11 14:57:00',14.4),(39,1,'2017-10-12 02:20:00',11.5),(40,1,'2017-10-12 14:43:00',9.2),(41,1,'2017-10-13 02:13:00',7),(42,1,'2017-10-13 14:52:00',5.5),(43,1,'2017-10-14 03:01:00',4.8),(44,1,'2017-10-19 18:03:00',4.8),(45,1,'2017-10-25 14:12:00',14.4),(46,1,'2017-10-26 04:23:00',11.1),(47,1,'2017-10-26 14:20:00',9),(48,1,'2017-10-27 04:07:00',6.6),(49,1,'2017-10-27 14:47:00',5.7),(50,1,'2017-10-28 02:52:00',4.8),(51,1,'2017-10-28 16:37:00',4.6),(52,1,'2017-11-09 04:18:00',12.4),(53,1,'2017-11-09 15:48:00',10.3),(54,1,'2017-11-10 04:56:00',8.1),(55,1,'2017-11-10 15:54:00',6.3),(56,1,'2017-11-11 04:00:00',5),(57,1,'2017-11-28 15:55:00',15.5),(58,1,'2017-11-29 02:56:00',11.8),(59,1,'2017-11-29 14:57:00',9.1),(60,1,'2017-11-30 04:11:00',7),(61,1,'2017-11-30 15:49:00',5.3),(62,1,'2017-11-30 20:02:00',4.9),(63,2,'2017-10-02 13:56:00',13),(64,2,'2017-10-03 04:35:00',10.6),(65,2,'2017-10-03 14:44:00',8.1),(66,2,'2017-10-04 03:23:00',5.1),(67,2,'2017-10-04 14:11:00',3.8),(68,2,'2017-10-05 03:29:00',3.5),(69,2,'2017-10-16 03:06:00',13.7),(70,2,'2017-10-16 15:00:00',11.2),(71,2,'2017-10-17 03:23:00',9.1),(72,2,'2017-10-17 14:42:00',8.1),(73,2,'2017-10-18 03:11:00',6.8),(74,2,'2017-10-18 14:00:00',6.1),(75,2,'2017-10-19 03:50:00',5.6),(76,2,'2017-10-19 14:29:00',5.4),(77,2,'2017-10-19 23:54:00',5.3),(78,2,'2017-11-07 06:04:00',15.1),(79,2,'2017-11-07 15:15:00',12.7),(80,2,'2017-11-08 05:54:00',9.2),(81,2,'2017-11-08 15:40:00',7.3),(82,2,'2017-11-09 04:16:00',5.4),(83,2,'2017-11-09 12:50:00',4.7),(84,2,'2017-11-09 15:47:00',4.6),(85,2,'2017-11-22 05:28:00',12.3),(86,2,'2017-11-22 15:36:00',10.1),(87,2,'2017-11-23 04:54:00',7.7),(88,2,'2017-11-23 19:53:00',6.2),(89,2,'2017-11-24 18:14:00',4.8),(90,2,'2017-11-25 01:58:00',4.8),(91,2,'2017-11-25 17:33:00',4.6),(92,3,'2017-10-11 14:57:00',63),(93,3,'2017-10-12 02:20:00',63),(94,3,'2017-10-12 14:43:00',63),(95,3,'2017-10-13 02:13:00',62.9),(96,3,'2017-10-13 14:52:00',63.2),(97,3,'2017-10-14 03:01:00',64.2),(98,3,'2017-10-19 18:03:00',32),(99,3,'2017-10-25 14:12:00',62.9),(100,3,'2017-10-26 04:23:00',65),(101,3,'2017-10-26 14:20:00',63),(102,3,'2017-10-27 04:07:00',63),(103,3,'2017-10-27 14:47:00',63),(104,3,'2017-10-28 02:52:00',64),(105,3,'2017-10-28 16:37:00',64),(106,3,'2017-11-01 05:00:00',32),(107,3,'2017-11-09 04:18:00',63),(108,3,'2017-11-09 15:48:00',63.2),(109,3,'2017-11-10 04:56:00',62.9),(110,3,'2017-11-10 15:54:00',63.2),(111,3,'2017-11-11 04:00:00',64.3),(112,3,'2017-11-15 18:17:00',32),(113,3,'2017-11-28 15:55:00',63),(114,3,'2017-11-29 02:56:00',63),(115,3,'2017-11-29 14:57:00',63),(116,3,'2017-11-30 04:11:00',63),(117,3,'2017-11-30 15:49:00',65.4),(118,4,'2017-10-02 13:56:00',62),(119,4,'2017-10-03 04:35:00',63),(120,4,'2017-10-03 14:44:00',63),(121,4,'2017-10-04 03:23:00',63),(122,4,'2017-10-04 14:11:00',63.4),(123,4,'2017-10-05 03:29:00',64),(124,4,'2017-10-09 13:00:00',32),(125,4,'2017-10-16 03:06:00',63.1),(126,4,'2017-10-16 15:00:00',61.5),(127,4,'2017-10-17 03:23:00',63),(128,4,'2017-10-17 14:42:00',63),(129,4,'2017-10-18 03:11:00',64.6),(130,4,'2017-10-18 14:00:00',65.9),(131,4,'2017-10-19 03:50:00',66.9),(132,4,'2017-10-19 14:29:00',67.2),(133,4,'2017-10-23 20:41:00',32),(134,4,'2017-11-07 06:04:00',63.5),(135,4,'2017-11-07 15:15:00',65),(136,4,'2017-11-08 05:54:00',65),(137,4,'2017-11-08 15:40:00',65.3),(138,4,'2017-11-09 04:16:00',66.9),(139,4,'2017-11-09 12:50:00',67.8),(140,4,'2017-11-09 15:47:00',68.1),(141,4,'2017-11-15 05:06:00',32),(142,4,'2017-11-22 05:28:00',65),(143,4,'2017-11-22 15:36:00',65.1),(144,4,'2017-11-23 04:54:00',65),(145,4,'2017-11-23 19:53:00',67.2),(146,4,'2017-11-24 18:14:00',68),(147,4,'2017-11-25 01:58:00',67.8),(148,4,'2017-11-25 17:33:00',68),(149,4,'2017-11-29 21:30:00',32),(150,1,'2017-12-01 21:11:21',16.7),(160,1,'2017-12-07 01:23:43',13.6969),(161,NULL,'2017-12-11 17:11:27',1),(162,NULL,'2017-12-11 17:34:41',1),(163,NULL,'2017-12-12 00:01:17',12.5);
/*!40000 ALTER TABLE `TagValue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `UnitOfMeasurement`
--

LOCK TABLES `UnitOfMeasurement` WRITE;
/*!40000 ALTER TABLE `UnitOfMeasurement` DISABLE KEYS */;
INSERT INTO `UnitOfMeasurement` VALUES (1,'bbl','barrel'),(2,'°F','degree Fahrenheit'),(3,'°C','degree Celsius'),(4,'°P','plato'),(5,'SG','specific gravity'),(6,'ADF','apparent degree of fermentation'),(7,'IBU','international bittering unit'),(8,'RE','real extract'),(9,'%','percent'),(10,'ppm','parts per million'),(11,'ae','ae'),(12,'°L','degree Lovibond'),(13,'min','minute'),(14,'s','second'),(15,'h','hour'),(16,'mm','millimeter'),(17,'gpm','gallons per minute'),(18,'t/h','tons per hour'),(19,': 1','ratio'),(20,'°F/min','degree Fahrenheit per minute'),(21,'g','grams'),(22,'lb','pound'),(23,'#','number'),(24,'x10^12 cells','x10^12 cells'),(25,'gal','gallon'),(26,'in','inches'),(27,'pH','potential of hydrogen'),(28,'x10^6 cells','x10^6 cells'),(29,'EBC','european brewery convention'),(30,'ppb','parts per billion'),(31,'abv','alcohol by volume'),(32,'lb/bbl','pounds / barrel'),(33,'cells/ml','cells per milliliter'),(34,'ASBC','American Society of Brewing Chemists'),(35,'vol','volumes'),(36,'cells/ml/°P','cells per ml per °P'),(37,'mg','milligram'),(38,'kg','kilogram'),(39,'mL','milliliter'),(40,'g/bbl','grams per barrel'),(41,'psi','pounds per square inch'),(42,'g/L','grams per liter'),(43,'SRM','Standard Reference Method');
/*!40000 ALTER TABLE `UnitOfMeasurement` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2017-12-16  9:00:29
