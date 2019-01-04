from flask import render_template
from flask_login import login_required
from . import physicalModels
from .. decorators import adminRequired
from .. models import Area, Enterprise, Site

modelName = "Physical Models"

@physicalModels.route("/physicalModels/select", methods = ["GET", "POST"]) # Default.
@physicalModels.route("/physicalModels/select/<string:selectedClass>", methods = ["GET", "POST"]) # Root.
@physicalModels.route("/physicalModels/select/<string:selectedClass>/<int:selectedId>", methods = ["GET", "POST"])
@login_required
@adminRequired
def selectPhysicalModel(selectedClass = None, selectedId = None):
	if selectedClass == None or selectedClass == "Root":
		parent = None
		children = Enterprise.query.order_by(Enterprise.Name)
		childrenClass = "Enterprise"
	elif selectedClass == "Enterprise":
		parent = Enterprise.query.get_or_404(selectedId)
		children = Site.query.filter_by(EnterpriseId = selectedId)
		childrenClass = "Site"
	elif selectedClass == "Site":
		parent = Site.query.get_or_404(selectedId)
		children = Area.query.filter_by(SiteId = selectedId)
		childrenClass = "Area"

	return render_template("physicalModels/select.html", children = children, childrenClass = childrenClass, parent = parent)
