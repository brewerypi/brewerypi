import subprocess
from flask import flash, redirect, url_for
from flask_login import login_required
from . import raspberryPiUtilities
from .. decorators import adminRequired

@raspberryPiUtilities.route("/reboot", methods = ["GET"])
@login_required
@adminRequired
def reboot():
	flash("Rebooting... Please wait. This will take approximately one minute.")
	command = "sleep 5 && sudo shutdown -r now"
	subprocess.Popen(command, shell = True)
	return redirect(url_for("home.homepage"))

@raspberryPiUtilities.route("/shutdown", methods = ["GET"])
@login_required
@adminRequired
def shutdown():
	flash("Shutting down... Please wait. This will take approximately one minute.<br>When the LEDs on the Raspberry Pi stop blinking, it should be safe to "\
		"unplug your Raspberry Pi.")
	command = "sleep 5 && sudo shutdown -h now"
	subprocess.Popen(command, shell = True)
	return redirect(url_for("home.homepage"))
