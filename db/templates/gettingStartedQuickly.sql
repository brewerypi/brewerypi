-- MySQL dump 10.16  Distrib 10.1.38-MariaDB, for debian-linux-gnueabihf (armv7l)
--
-- Host: localhost    Database: BreweryPi
-- ------------------------------------------------------
-- Server version	10.1.38-MariaDB-0+deb9u1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
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
INSERT INTO `Area` (`AreaId`, `Abbreviation`, `Description`, `Name`, `SiteId`) VALUES (1,'C','','Cellar',1);
/*!40000 ALTER TABLE `Area` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Element`
--

LOCK TABLES `Element` WRITE;
/*!40000 ALTER TABLE `Element` DISABLE KEYS */;
INSERT INTO `Element` (`ElementId`, `Description`, `ElementTemplateId`, `Name`, `TagAreaId`) VALUES (1,'',1,'FV01',1),(2,'',1,'FV02',1),(3,'',1,'FV03',1),(4,'',2,'BBT01',1),(5,'',2,'BBT02',1);
/*!40000 ALTER TABLE `Element` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `ElementAttribute`
--

LOCK TABLES `ElementAttribute` WRITE;
/*!40000 ALTER TABLE `ElementAttribute` DISABLE KEYS */;
INSERT INTO `ElementAttribute` (`ElementAttributeId`, `ElementAttributeTemplateId`, `ElementId`, `TagId`) VALUES (1,5,1,1),(2,6,1,2),(3,7,1,3),(4,8,1,4),(5,5,2,5),(6,6,2,6),(7,7,2,7),(8,8,2,8),(9,5,3,9),(10,6,3,10),(11,7,3,11),(12,8,3,12),(13,1,4,13),(14,2,4,14),(15,3,4,15),(16,4,4,16),(17,1,5,17),(18,2,5,18),(19,3,5,19),(20,4,5,20);
/*!40000 ALTER TABLE `ElementAttribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `ElementAttributeTemplate`
--

LOCK TABLES `ElementAttributeTemplate` WRITE;
/*!40000 ALTER TABLE `ElementAttributeTemplate` DISABLE KEYS */;
INSERT INTO `ElementAttributeTemplate` (`ElementAttributeTemplateId`, `Description`, `ElementTemplateId`, `LookupId`, `Name`, `UnitOfMeasurementId`) VALUES (1,'',2,1,'Brand',NULL),(2,'',2,2,'State',NULL),(3,'',2,NULL,'CO2',39),(4,'',2,NULL,'Temperature',8),(5,'',1,1,'Brand',NULL),(6,'',1,2,'State',NULL),(7,'',1,NULL,'Temperature',8),(8,'',1,NULL,'Plato',7);
/*!40000 ALTER TABLE `ElementAttributeTemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `ElementTemplate`
--

LOCK TABLES `ElementTemplate` WRITE;
/*!40000 ALTER TABLE `ElementTemplate` DISABLE KEYS */;
INSERT INTO `ElementTemplate` (`ElementTemplateId`, `Description`, `Name`, `SiteId`) VALUES (1,'Fermenting Vessel','FV',1),(2,'Brite Beer Tank','BBT',1);
/*!40000 ALTER TABLE `ElementTemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Enterprise`
--

LOCK TABLES `Enterprise` WRITE;
/*!40000 ALTER TABLE `Enterprise` DISABLE KEYS */;
INSERT INTO `Enterprise` (`EnterpriseId`, `Abbreviation`, `Description`, `Name`) VALUES (1,'MC','','My Company');
/*!40000 ALTER TABLE `Enterprise` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `EventFrameAttribute`
--

LOCK TABLES `EventFrameAttribute` WRITE;
/*!40000 ALTER TABLE `EventFrameAttribute` DISABLE KEYS */;
INSERT INTO `EventFrameAttribute` (`EventFrameAttributeId`, `ElementId`, `EventFrameAttributeTemplateId`, `TagId`) VALUES (1,1,1,1),(2,1,2,2),(3,1,3,3),(4,1,4,4),(5,2,1,5),(6,2,2,6),(7,2,3,7),(8,2,4,8),(9,3,1,9),(10,3,2,10),(11,3,3,11),(12,3,4,12),(13,4,5,13),(14,4,6,14),(15,4,7,16),(16,4,8,15),(17,5,5,17),(18,5,6,18),(19,5,7,20),(20,5,8,19);
/*!40000 ALTER TABLE `EventFrameAttribute` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `EventFrameAttributeTemplate`
--

LOCK TABLES `EventFrameAttributeTemplate` WRITE;
/*!40000 ALTER TABLE `EventFrameAttributeTemplate` DISABLE KEYS */;
INSERT INTO `EventFrameAttributeTemplate` (`EventFrameAttributeTemplateId`, `Description`, `DefaultEndValue`, `DefaultStartValue`, `EventFrameTemplateId`, `LookupId`, `Name`, `UnitOfMeasurementId`) VALUES (1,'',NULL,NULL,1,1,'Brand',NULL),(2,'',1,0,1,2,'State',NULL),(3,'',NULL,NULL,1,NULL,'Temperature',8),(4,'',NULL,NULL,1,NULL,'Plato',7),(5,'',NULL,NULL,2,1,'Brand',NULL),(6,'',1,4,2,2,'State',NULL),(7,'',NULL,NULL,2,NULL,'Temperature',8),(8,'',NULL,NULL,2,NULL,'CO2',39);
/*!40000 ALTER TABLE `EventFrameAttributeTemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `EventFrameTemplate`
--

LOCK TABLES `EventFrameTemplate` WRITE;
/*!40000 ALTER TABLE `EventFrameTemplate` DISABLE KEYS */;
INSERT INTO `EventFrameTemplate` (`EventFrameTemplateId`, `Description`, `ElementTemplateId`, `Name`, `Order`, `ParentEventFrameTemplateId`) VALUES (1,'',1,'Fermentation',1,NULL),(2,'',2,'Brite Beer Storage',1,NULL);
/*!40000 ALTER TABLE `EventFrameTemplate` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Lookup`
--

LOCK TABLES `Lookup` WRITE;
/*!40000 ALTER TABLE `Lookup` DISABLE KEYS */;
INSERT INTO `Lookup` (`LookupId`, `EnterpriseId`, `Name`) VALUES (1,1,'Brands'),(2,1,'Status');
/*!40000 ALTER TABLE `Lookup` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `LookupValue`
--

LOCK TABLES `LookupValue` WRITE;
/*!40000 ALTER TABLE `LookupValue` DISABLE KEYS */;
INSERT INTO `LookupValue` (`LookupValueId`, `Name`, `Selectable`, `LookupId`, `Value`) VALUES (1,'Porter',1,1,0),(2,'Pale Ale',1,1,1),(3,'IPA',1,1,2),(4,'Fermentation',1,2,0),(5,'Empty',1,2,1),(6,'CIP',1,2,2),(7,'Ready for Packaging',1,2,3),(8,'Pre-Package',1,2,4),(9,'Lager',1,1,3),(10,'Winter Ale',1,1,4);
/*!40000 ALTER TABLE `LookupValue` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Site`
--

LOCK TABLES `Site` WRITE;
/*!40000 ALTER TABLE `Site` DISABLE KEYS */;
INSERT INTO `Site` (`SiteId`, `Abbreviation`, `Description`, `EnterpriseId`, `Name`) VALUES (1,'MS','',1,'My Site');
/*!40000 ALTER TABLE `Site` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `Tag`
--

LOCK TABLES `Tag` WRITE;
/*!40000 ALTER TABLE `Tag` DISABLE KEYS */;
INSERT INTO `Tag` (`TagId`, `AreaId`, `Description`, `LookupId`, `Name`, `UnitOfMeasurementId`) VALUES (1,1,'',1,'FV01_Brand',NULL),(2,1,'',2,'FV01_State',NULL),(3,1,'',NULL,'FV01_Temperature',8),(4,1,'',NULL,'FV01_Plato',7),(5,1,'',1,'FV02_Brand',NULL),(6,1,'',2,'FV02_State',NULL),(7,1,'',NULL,'FV02_Temperature',8),(8,1,'',NULL,'FV02_Plato',7),(9,1,'',1,'FV03_Brand',NULL),(10,1,'',2,'FV03_State',NULL),(11,1,'',NULL,'FV03_Temperature',8),(12,1,'',NULL,'FV03_Plato',7),(13,1,'',1,'BBT01_Brand',NULL),(14,1,'',2,'BBT01_State',NULL),(15,1,'',NULL,'BBT01_CO2',39),(16,1,'',NULL,'BBT01_Temperature',8),(17,1,'',1,'BBT02_Brand',NULL),(18,1,'',2,'BBT02_State',NULL),(19,1,'',NULL,'BBT02_CO2',39),(20,1,'',NULL,'BBT02_Temperature',8);
/*!40000 ALTER TABLE `Tag` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Dumping data for table `UnitOfMeasurement`
--

LOCK TABLES `UnitOfMeasurement` WRITE;
/*!40000 ALTER TABLE `UnitOfMeasurement` DISABLE KEYS */;
INSERT INTO `UnitOfMeasurement` (`UnitOfMeasurementId`, `Abbreviation`, `Name`) VALUES (27,'%','percentage'),(2,'ADF','apparent degree of fermentation'),(1,'ASBC','american society of brewing chemists'),(3,'bbl','barrel'),(4,'cells/ml','cells per milliliter'),(5,'cells/ml/°P','cells per ml per degree plato'),(10,'EBC','european brewery convention'),(13,'g','grams'),(14,'g/bbl','grams per barrel'),(15,'g/L','grams per liter'),(11,'gal','gallon'),(12,'gpm','gallons per minute'),(16,'h','hour'),(18,'IBU','international bittering unit'),(17,'in','inches'),(19,'kg','kilogram'),(20,'L','liters'),(29,'lb','pound'),(30,'lb/bbl','pounds per barrel'),(21,'mg','milligram'),(24,'min','minute'),(22,'mL','milliliter'),(23,'mm','millimeter'),(28,'pH','potential of hydrogen'),(25,'ppb','parts per billion'),(26,'ppm','parts per million'),(31,'psi','pounds per square inch'),(32,'RDF','real degree of fermentation'),(33,'RE','real extract'),(34,'s','second'),(35,'SG','specific gravity'),(36,'SRM','standard reference method'),(37,'t/h','tons per hour'),(38,'TA','total acidity'),(39,'vol','volumes'),(40,'x10^12 cells','x10^12 cells'),(41,'x10^6 cells','x10^6 cells'),(6,'°C','degree celsius'),(8,'°F','degree fahrenheit'),(9,'°F/min','degree fahrenheit per minute'),(7,'°P','degree plato');
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

-- Dump completed on 2019-06-19  5:00:17
