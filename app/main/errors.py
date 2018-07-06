from flask import render_template
from . import main
from .. import db

@main.app_errorhandler(403)
def forbidden(e):
    return render_template("403.html"), 403

@main.app_errorhandler(404)
def notFound(e):
    return render_template("404.html"), 404

@main.app_errorhandler(500)
def internalServerError(e):
    # Rollback the session in case of database exception as base.html requires a session.
    db.session.rollback()
    return render_template("500.html"), 500
