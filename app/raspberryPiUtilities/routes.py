import os
import subprocess
from datetime import datetime
from flask import current_app, flash, Markup, redirect, render_template, send_file, url_for
from flask_login import login_required
from . import raspberryPiUtilities
from .. decorators import adminRequired

@raspberryPiUtilities.route("/backupDatabase", methods = ["GET"])
@login_required
@adminRequired
def backupDatabase():
	attachmentFilename = datetime.now().strftime("%Y%m%d%H%M") + "-BreweryPi.sql" 
	command = "sudo mysqldump --complete-insert=TRUE {} > /home/pi/brewerypi/exports/BreweryPi.sql".format(current_app.config["MYSQL_DATABASE"])
	p = subprocess.Popen(command, shell = True)
	p.wait()
	return send_file(os.path.join("..", current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_DATABASE_FILENAME"]), as_attachment = True,
		attachment_filename = attachmentFilename)

@raspberryPiUtilities.route("/info", methods = ["GET"])
@login_required
@adminRequired
def info():
	ipCommand = "ip a"
	ipOutput = subprocess.check_output(ipCommand, shell = True).decode("utf-8").replace("\n", "<br>")
	uptimeCommand = "uptime -p"
	uptimeOutput = subprocess.check_output(uptimeCommand, shell = True).decode("utf-8")
	return render_template("raspberryPiUtilities/info.html", ipOutput = ipOutput, uptimeOutput = uptimeOutput)

@raspberryPiUtilities.route("/reboot", methods = ["GET"])
@login_required
@adminRequired
def reboot():
	flash("Rebooting... Please wait. This will take approximately one minute.")
	command = "sleep 5 && sudo shutdown -r now"
	subprocess.Popen(command, shell = True)
	return redirect(url_for("main.index"))

@raspberryPiUtilities.route("/shutdown", methods = ["GET"])
@login_required
@adminRequired
def shutdown():
	flash(Markup("Shutting down... Please wait. This will take approximately one minute.<br>When the LEDs on the Raspberry Pi stop blinking, it should be " \
		"safe to unplug your Raspberry Pi."))
	command = "sleep 5 && sudo shutdown -h now"
	subprocess.Popen(command, shell = True)
	return redirect(url_for("main.index"))
