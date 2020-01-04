from os import getcwd
from flask import render_template
from git import Repo
from . import main

@main.route("/")
def index():
	repository = Repo(getcwd())
	tagName = ""
	for tag in repository.tags:
		if tag.commit == repository.head.commit:
			tagName = tag.name
			break

	if tagName == "":
		branch = repository.active_branch
		version = branch.name
	else:
		version = tagName

	return render_template("main/index.html", version = version)
