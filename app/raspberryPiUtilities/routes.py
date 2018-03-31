import subprocess
from flask import flash, redirect, url_for
from flask_login import login_required
from . import raspberryPiUtilities
from .. decorators import adminRequired

@raspberryPiUtilities.route("/reboot", methods = ["GET", "POST"])
@login_required
@adminRequired
def reboot():
	flash("Rebooting... Please wait. This will take approximately one minute.")
	subprocess.call(["sudo", "reboot"])
	return redirect(url_for("home.homepage"))
