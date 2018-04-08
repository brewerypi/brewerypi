from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from config import Config

boostrap = Bootstrap()
db = SQLAlchemy()
loginManager = LoginManager()
loginManager.session_protection = "basic"
loginManager.login_view = "authentications.login"
migrate = Migrate()

def create_app(configClass = Config):
	app = Flask(__name__)
	app.config.from_object(configClass)

	boostrap.init_app(app)
	db.init_app(app)
	loginManager.init_app(app)
	migrate.init_app(app, db, directory = "db/migrations")

	from . areas import areas as areasBlueprint
	app.register_blueprint(areasBlueprint)

	from . attributeTemplates import attributeTemplates as attributeTemplatesBlueprint
	app.register_blueprint(attributeTemplatesBlueprint)

	from . authentications import authentications as authenticationsBlueprint
	app.register_blueprint(authenticationsBlueprint)

	from . elements import elements as elementsBlueprint
	app.register_blueprint(elementsBlueprint)

	from . elementAttributes import elementAttributes as elementAttributesBlueprint
	app.register_blueprint(elementAttributesBlueprint)

	from . elementTemplates import elementTemplates as elementTemplatesBlueprint
	app.register_blueprint(elementTemplatesBlueprint)

	from . enterprises import enterprises as enterprisesBlueprint
	app.register_blueprint(enterprisesBlueprint)

	from . eventFrames import eventFrames as eventFramesBlueprint
	app.register_blueprint(eventFramesBlueprint)

	from . eventFrameTemplates import eventFrameTemplates as eventFrameTemplatesBlueprint
	app.register_blueprint(eventFrameTemplatesBlueprint)

	from . lookups import lookups as lookupsBlueprint
	app.register_blueprint(lookupsBlueprint)

	from . lookupValues import lookupValues as lookupValuesBlueprint
	app.register_blueprint(lookupValuesBlueprint)

	from . main import main as mainBlueprint
	app.register_blueprint(mainBlueprint)

	from . tags import tags as tagsBlueprint
	app.register_blueprint(tagsBlueprint)

	from . tagValues import tagValues as tagValuesBlueprint
	app.register_blueprint(tagValuesBlueprint)

	from . sites import sites as sitesBlueprint
	app.register_blueprint(sitesBlueprint)

	from . unitOfMeasurements import unitOfMeasurements as unitOfMeasurementsBlueprint
	app.register_blueprint(unitOfMeasurementsBlueprint)

	from . users import users as usersBlueprint
	app.register_blueprint(usersBlueprint)

	return app
