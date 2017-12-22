import os
from dotenv import load_dotenv

class Config:
	SECRET_KEY = os.environ.get("SECRET_KEY") or "p9Bv<3Eid9%$i01"
	SQLALCHEMY_DATABASE_URI = os.environ.get("SECRET_KEY") or "mysql://pi:brewery@localhost/BreweryPiDemo1"
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	TAG_IMPORT_FILE_PATH = "imports/tags.csv"
