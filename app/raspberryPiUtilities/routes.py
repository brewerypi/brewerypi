import os
import subprocess
from datetime import datetime
from flask import current_app, flash, Markup, redirect, send_file, url_for
from flask_login import login_required
from . import raspberryPiUtilities
from .. decorators import adminRequired

@raspberryPiUtilities.route("/backupDatabase", methods = ["GET"])
@login_required
@adminRequired
def backupDatabase(): 
	attachmentFilename = datetime.now().strftime("%Y%m%d%H%M") + "-BreweryPi.sql" 
	command = "sudo mysqldump --complete-insert=TRUE BreweryPi > ~/brewerypi/exports/BreweryPi.sql"
	p = subprocess.Popen(command, shell = True)
	p.wait()
	return send_file(os.path.join("..", current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_DATABASE_FILENAME"]), as_attachment = True,
		attachment_filename = attachmentFilename)

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
	flash(Markup("Shutting down... Please wait. This will take approximately one minute.<br>When the LEDs on the Raspberry Pi stop blinking, it should be " \
		"safe to unplug your Raspberry Pi."))
	command = "sleep 5 && sudo shutdown -h now"
	subprocess.Popen(command, shell = True)
	return redirect(url_for("home.homepage"))
