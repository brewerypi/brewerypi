import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))

class Config:
	BOOTSTRAP_SERVE_LOCAL = True
	EXPORT_FOLDER = "exports"
	EXPORT_DATABASE_FILENAME = "BreweryPi.sql"
	EXPORT_ELEMENT_ATTRIBUTES_FILENAME = "elementsAttributes.csv"
	EXPORT_TAGS_FILENAME = "tags.csv"
	IMPORT_FOLDER = "imports"
	IMPORT_ELEMENT_ATTRIBUTES_FILENAME = "elementAttributes.csv"
	IMPORT_TAGS_FILENAME = "tags.csv"
	SECRET_KEY = os.environ.get("SECRET_KEY") or "p9Bv<3Eid9%$i01"
	SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI") or "mysql://pi:brewery@localhost/BreweryPiDemo1"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
