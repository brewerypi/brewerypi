import os

class Config:
	SQLALCHEMY_TRACK_MODIFICATIONS = False 
	SECRET_KEY = "p9Bv<3Eid9%$i01"

	@staticmethod
	def init_app(app):
		pass

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = "mysql://pi:brewery@localhost/BreweryPiDemo1"

class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = "mysql://pi:brewery@localhost/BreweryPi"

config = \
{
	"development" : DevelopmentConfig,
	"production" : ProductionConfig,
	"default" : DevelopmentConfig
}
