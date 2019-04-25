import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
	BOOTSTRAP_SERVE_LOCAL = True
	EXPORT_DATABASE_FILENAME = "BreweryPi.sql"
	EXPORT_ELEMENT_ATTRIBUTES_FILENAME = "elementsAttributes.csv"
	EXPORT_EVENT_FRAME_ATTRIBUTES_FILENAME = "eventFrameAttributes.csv"
	EXPORT_FOLDER = "exports"
	EXPORT_TAGS_FILENAME = "tags.csv"
	GRAFANA_BASE_URI = os.environ.get("GRAFANA_BASE_URI") or "/grafana"
	IMPORT_DATABASE_FILENAME = "BreweryPi.sql"
	IMPORT_ELEMENT_ATTRIBUTES_FILENAME = "elementAttributes.csv"
	IMPORT_EVENT_FRAME_ATTRIBUTES_FILENAME = "eventFrameAttributes.csv"
	IMPORT_FOLDER = "imports"
	IMPORT_TAGS_FILENAME = "tags.csv"
	IS_RASPBERRY_PI = True if os.environ.get("IS_RASPBERRY_PI") == "1" else False
	LOCAL_TIMEZONE = os.environ.get("LOCAL_TIMEZONE")
	MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE") or "BreweryPi"
	NOTIFICATIONS_INTERVAL_IN_MILLISECONDS = os.environ.get("NOTIFICATIONS_INTERVAL") or 10000
	SECRET_KEY = os.environ.get("SECRET_KEY") or "Replace with a hard to guess string."
	SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or "mysql://pi:brewery@localhost/BreweryPi"
	SQLALCHEMY_SERVER_URI = os.environ.get("SQLALCHEMY_SERVER_URI") or "mysql://pi:brewery@localhost"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
