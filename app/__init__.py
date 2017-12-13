from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

from config import config

boostrap = Bootstrap()
db = SQLAlchemy()

def create_app(config_name):

	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	boostrap.init_app(app)
	db.init_app(app)

	from .admin import admin as admin_blueprint
	app.register_blueprint(admin_blueprint, url_prefix='/admin')

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from . elements import elements as elementsBlueprint
	app.register_blueprint(elementsBlueprint)

	from . elementAttributes import elementAttributes as elementAttributesBlueprint
	app.register_blueprint(elementAttributesBlueprint)

	from .home import home as home_blueprint
	app.register_blueprint(home_blueprint)

	from . lookups import lookups as lookupsBlueprint
	app.register_blueprint(lookupsBlueprint)

	from . lookupValues import lookupValues as lookupValuesBlueprint
	app.register_blueprint(lookupValuesBlueprint)

	from . tags import tags as tagsBlueprint
	app.register_blueprint(tagsBlueprint)

	from . tagValues import tagValues as tagValuesBlueprint
	app.register_blueprint(tagValuesBlueprint)

	return app
