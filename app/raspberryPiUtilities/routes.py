import os
import subprocess
from datetime import datetime
from flask import current_app, flash, redirect, render_template, send_file, url_for
from flask_login import login_required
from markupsafe import Markup
from . import raspberryPiUtilities
from .. import db
from . forms import DatabaseBackupImportForm
from .. decorators import adminRequired

@raspberryPiUtilities.route("/backupDatabase", methods = ["GET"])
@login_required
@adminRequired
def backupDatabase():
	attachmentFilename = datetime.utcnow().strftime("%Y%m%d%H%M") + "-BreweryPi.sql" 
	command = "sudo mysqldump --complete-insert=TRUE {} > {}/{}/BreweryPi.sql".format(current_app.config["MYSQL_DATABASE"],
		os.path.dirname(current_app.instance_path), current_app.config["EXPORT_FOLDER"])
	process = subprocess.Popen(command, shell = True)
	process.wait()
	return send_file(os.path.join("..", current_app.config["EXPORT_FOLDER"], current_app.config["EXPORT_DATABASE_FILENAME"]), as_attachment = True,
		attachment_filename = attachmentFilename)

@raspberryPiUtilities.route("/info", methods = ["GET"])
@login_required
@adminRequired
def info():
	freeCommand = "free -h"
	freeOutput = subprocess.check_output(freeCommand, shell = True).decode("utf-8")
	ipCommand = "ip a"
	ipOutput = subprocess.check_output(ipCommand, shell = True).decode("utf-8")
	uptimeCommand = "uptime -p"
	uptimeOutput = subprocess.check_output(uptimeCommand, shell = True).decode("utf-8")
	return render_template("raspberryPiUtilities/info.html", freeOutput = freeOutput, ipOutput = ipOutput, uptimeOutput = uptimeOutput)

@raspberryPiUtilities.route("/reboot", methods = ["GET"])
@login_required
@adminRequired
def reboot():
	flash("Rebooting... Please wait. This will take approximately one minute.")
	command = "sleep 5 && sudo shutdown -r now"
	subprocess.Popen(command, shell = True)
	return redirect(url_for("main.index"))

@raspberryPiUtilities.route("/restoreDatabase", methods = ["GET", "POST"])
@login_required
@adminRequired
def restoreDatabase():
	form = DatabaseBackupImportForm()
	errors = []
	successes = []

	if form.validate_on_submit():
		# Save a version of the uploaded file.
		databaseBackupFile = form.databaseBackupFile.data
		databaseBackupFile.save(os.path.join(current_app.config["IMPORT_FOLDER"], current_app.config["IMPORT_DATABASE_FILENAME"]))
		databaseBackupFile.close()
		db.session.close()
		command = "sudo mysql BreweryPi < {}/{}/BreweryPi.sql".format(os.path.dirname(current_app.instance_path), current_app.config["IMPORT_FOLDER"])
		try:
			subprocess.check_output(command, shell = True, stderr = subprocess.STDOUT)
			successes.append("Database successfully restored.")
		except subprocess.CalledProcessError as exception:
			errors.append("Database restored failed. Error message: {}".format(exception.output.decode()))

	return render_template("import.html", errors = errors, form = form, importing = "Database Backup", successes = successes)
	
@raspberryPiUtilities.route("/shutdown", methods = ["GET"])
@login_required
@adminRequired
def shutdown():
	flash(Markup("Shutting down... Please wait. This will take approximately one minute.<br>When the LEDs on the Raspberry Pi stop blinking, it should be " \
		"safe to unplug your Raspberry Pi."))
	command = "sleep 5 && sudo shutdown -h now"
	subprocess.Popen(command, shell = True)
	return redirect(url_for("main.index"))
