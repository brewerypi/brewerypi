import dash
from flask import Flask
from flask.helpers import get_root_path
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_required
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import Config

boostrap = Bootstrap()
db = SQLAlchemy()
loginManager = LoginManager()
loginManager.session_protection = "basic"
loginManager.login_view = "authentications.login"
moment = Moment()

def createApp(configClass = Config):
	app = Flask(__name__)
	app.config.from_object(configClass)

	from app.activeEventFramesSummaryDash.layout import layout as activeEventFramesSummaryDashLayout
	from app.activeEventFramesSummaryDash.callbacks import registerCallbacks as activeEventFramesSummaryDashCallbacks
	registerDashApp(app, "activeEventFramesSummaryDash", activeEventFramesSummaryDashLayout, activeEventFramesSummaryDashCallbacks,
		"Active Event Frames Summary Dash")

	from app.elementSummaryDash.layout import layout as elementSummaryDashLayout
	from app.elementSummaryDash.callbacks import registerCallbacks as elementSummaryDashCallbacks
	registerDashApp(app, "elementSummaryDash", elementSummaryDashLayout, elementSummaryDashCallbacks, "Element Summary Dash")

	from app.elementValuesGraphDash.layout import layout as elementValuesGraphDashLayout
	from app.elementValuesGraphDash.callbacks import registerCallbacks as elementValuesGraphDashCallbacks
	registerDashApp(app, "elementValuesGraphDash", elementValuesGraphDashLayout, elementValuesGraphDashCallbacks, "Element Values Graph Dash")

	from app.eventFrameGroupSummaryDash.layout import layout as eventFrameGroupSummaryDashLayout
	from app.eventFrameGroupSummaryDash.callbacks import registerCallbacks as eventFrameGroupSummaryDashCallbacks
	registerDashApp(app, "eventFrameGroupSummaryDash", eventFrameGroupSummaryDashLayout, eventFrameGroupSummaryDashCallbacks, "Event Frame Group Summary Dash")

	from app.eventFramesGraphDash.layout import layout as eventFramesGraphDashLayout
	from app.eventFramesGraphDash.callbacks import registerCallbacks as eventFramesGraphDashCallbacks
	registerDashApp(app, "eventFramesGraphDash", eventFramesGraphDashLayout, eventFramesGraphDashCallbacks, "Event Frames Graph Dash")

	from app.eventFramesOverlayDash.layout import layout as eventFramesOverlayDashLayout
	from app.eventFramesOverlayDash.callbacks import registerCallbacks as eventFramesOverlayDashCallbacks
	registerDashApp(app, "eventFramesOverlayDash", eventFramesOverlayDashLayout, eventFramesOverlayDashCallbacks, "Event Frames Overlay Dash")

	from app.tagValuesGraphDash.layout import layout as tagValuesGraphDashLayout
	from app.tagValuesGraphDash.callbacks import registerCallbacks as tagValuesGraphDashCallbacks
	registerDashApp(app, "tagValuesGraphDash", tagValuesGraphDashLayout, tagValuesGraphDashCallbacks, "Tag Values Graph Dash")

	boostrap.init_app(app)
	db.init_app(app)
	loginManager.init_app(app)
	moment.init_app(app)

	from . areas import areas as areasBlueprint
	app.register_blueprint(areasBlueprint)

	from . authentications import authentications as authenticationsBlueprint
	app.register_blueprint(authenticationsBlueprint)

	from . customTemplateFilters import customTemplateFilters as customTemplateFiltersBlueprint
	app.register_blueprint(customTemplateFiltersBlueprint)

	from . dash import dash as dashBlueprint
	app.register_blueprint(dashBlueprint)

	from . elements import elements as elementsBlueprint
	app.register_blueprint(elementsBlueprint)

	from . elementAttributes import elementAttributes as elementAttributesBlueprint
	app.register_blueprint(elementAttributesBlueprint)

	from . elementAttributeTemplates import elementAttributeTemplates as elementAttributeTemplatesBlueprint
	app.register_blueprint(elementAttributeTemplatesBlueprint)

	from . elementTemplates import elementTemplates as elementTemplatesBlueprint
	app.register_blueprint(elementTemplatesBlueprint)

	from . enterprises import enterprises as enterprisesBlueprint
	app.register_blueprint(enterprisesBlueprint)

	from . eventFrameAttributes import eventFrameAttributes as eventFrameAttributesBlueprint
	app.register_blueprint(eventFrameAttributesBlueprint)

	from . eventFrameAttributeTemplates import eventFrameAttributeTemplates as eventFrameAttributeTemplatesBlueprint
	app.register_blueprint(eventFrameAttributeTemplatesBlueprint)

	from . eventFrameEventFrameGroups import eventFrameEventFrameGroups as eventFrameEventFrameGroupsBlueprint
	app.register_blueprint(eventFrameEventFrameGroupsBlueprint)

	from . eventFrameGroups import eventFrameGroups as eventFrameGroupsBlueprint
	app.register_blueprint(eventFrameGroupsBlueprint)

	from . eventFrameNotes import eventFrameNotes as eventFrameNotesBlueprint
	app.register_blueprint(eventFrameNotesBlueprint)

	from . eventFrames import eventFrames as eventFramesBlueprint
	app.register_blueprint(eventFramesBlueprint)

	from . eventFrameTemplates import eventFrameTemplates as eventFrameTemplatesBlueprint
	app.register_blueprint(eventFrameTemplatesBlueprint)

	from . eventFrameTemplateViews import eventFrameTemplateViews as eventFrameTemplateViewsBlueprint
	app.register_blueprint(eventFrameTemplateViewsBlueprint)

	from . lookups import lookups as lookupsBlueprint
	app.register_blueprint(lookupsBlueprint)

	from . lookupValues import lookupValues as lookupValuesBlueprint
	app.register_blueprint(lookupValuesBlueprint)

	from . main import main as mainBlueprint
	app.register_blueprint(mainBlueprint)

	from . messages import messages as messagesBlueprint
	app.register_blueprint(messagesBlueprint)

	from . notifications import notifications as notificationsBlueprint
	app.register_blueprint(notificationsBlueprint)

	from . physicalModels import physicalModels as physicalModelsBlueprint
	app.register_blueprint(physicalModelsBlueprint)

	from . raspberryPiUtilities import raspberryPiUtilities as raspberryPiUtilitiesBlueprint
	app.register_blueprint(raspberryPiUtilitiesBlueprint)

	from . sites import sites as sitesBlueprint
	app.register_blueprint(sitesBlueprint)

	from . tags import tags as tagsBlueprint
	app.register_blueprint(tagsBlueprint)

	from . tagValueNotes import tagValueNotes as tagValueNotesBlueprint
	app.register_blueprint(tagValueNotesBlueprint)

	from . tagValues import tagValues as tagValuesBlueprint
	app.register_blueprint(tagValuesBlueprint)

	from . unitOfMeasurements import unitOfMeasurements as unitOfMeasurementsBlueprint
	app.register_blueprint(unitOfMeasurementsBlueprint)

	from . users import users as usersBlueprint
	app.register_blueprint(usersBlueprint)

	return app

def registerDashApp(app, urlBasePathname, layout, registerCallbacks, title):
	dashApp = dash.Dash \
	(
		__name__,
		assets_folder = "{}/{}/assets/".format(get_root_path(__name__), urlBasePathname),
		external_stylesheets = ["/static/bootstrap/css/bootstrap.min.css"],
		external_scripts = ["/static/bootstrap/jquery.min.js", "/static/bootstrap/js/bootstrap.min.js"],
		server = app,
		url_base_pathname = "/{}/".format(urlBasePathname)
	)

	dashApp.layout = layout
	dashApp.title = title
	registerCallbacks(dashApp)
	protectDashviews(dashApp)

def protectDashviews(dashApp):
	for viewFunction in dashApp.server.view_functions:
		if viewFunction.startswith(dashApp.config.url_base_pathname):
			dashApp.server.view_functions[viewFunction] = login_required(dashApp.server.view_functions[viewFunction])
