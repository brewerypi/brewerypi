# app/admin/views.py

from flask import abort, flash, redirect, render_template, request, url_for
# from flask_login import current_user, login_required

from . import admin

from . forms import AreaForm, AttributeTemplateForm, ElementAttributeForm, ElementForm, EventFrameForm, ElementTemplateForm, EnterpriseForm, \
	EventFrameTemplateForm, LookupForm, LookupValueForm, SiteForm, TagForm, TagValueForm, UnitOfMeasurementForm

from .. import db

from .. models import Area, AttributeTemplate, Element, ElementAttribute, ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, Lookup, LookupValue, \
	Site, Tag, TagValue, UnitOfMeasurement

# def check_admin():
# 	"""
# 	Prevent non-admins from accessing the page
# 	"""
# 	if not current_user.is_admin:
# 		abort(403)

################################################################################
# Area views.
################################################################################

@admin.route('/areas', methods=['GET', 'POST'])
# @login_required
def list_areas():
	# check_admin()

	areas = Area.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Name)

	return render_template('admin/areas/areas.html', areas=areas)

@admin.route('/areas/add', methods=['GET', 'POST'])
# @login_required
def add_area():
	# check_admin()

	add_area = True

	form = AreaForm()

	# Add a new area.
	if form.validate_on_submit():
		area = Area(Site=form.site.data, Name=form.name.data, Abbreviation=form.abbreviation.data, Description=form.description.data)
		db.session.add(area)
		db.session.commit()
		flash('You have successfully added a new area.')

		return redirect(url_for('admin.list_areas'))

	# Present a form to add a new area.
	return render_template('admin/areas/area.html', add_area=add_area, form=form)

@admin.route('/areas/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_area(id):
	# check_admin()

	area = Area.query.get_or_404(id)
	db.session.delete(area)
	db.session.commit()
	flash('You have successfully deleted the area.')

	return redirect(url_for('admin.list_areas'))

@admin.route('/areas/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_area(id):
	# check_admin()

	add_area = False

	area = Area.query.get_or_404(id)
	form = AreaForm(obj=area)

	# Edit an existing area.
	if form.validate_on_submit():
		area.Site = form.site.data
		area.Name = form.name.data
		area.Abbreviation = form.abbreviation.data
		area.Description = form.description.data

		db.session.commit()

		flash('You have successfully edited the area.')

		return redirect(url_for('admin.list_areas'))

	# Present a form to edit an existing area.
	form.site.data = area.Site
	form.name.data = area.Name
	form.abbreviation.data = area.Abbreviation
	form.description.data = area.Description
	return render_template('admin/areas/area.html', add_area=add_area, form=form, area=area)

################################################################################
# Attribute Template views.
################################################################################

@admin.route('/attributeTemplates', methods=['GET', 'POST'])
# @login_required
def list_attributeTemplates():
	# check_admin()

	attributeTemplates = AttributeTemplate.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, AttributeTemplate.Name)

	return render_template('admin/attributeTemplates/attributeTemplates.html', attributeTemplates=attributeTemplates)

@admin.route('/attributeTemplates/add', methods=['GET', 'POST'])
# @login_required
def add_attributeTemplate():
	# check_admin()

	add_attributeTemplate = True

	form = AttributeTemplateForm()

	# Add a new attributeTemplate.
	if form.validate_on_submit():
		attributeTemplate = AttributeTemplate(ElementTemplate=form.elementTemplate.data, Name=form.name.data, Description=form.description.data)
		db.session.add(attributeTemplate)
		db.session.commit()
		flash('You have successfully added a new attribute template.')

		return redirect(url_for('admin.list_attributeTemplates'))

	# Present a form to add a new attribute template.
	return render_template('admin/attributeTemplates/attributeTemplate.html', add_attributeTemplate=add_attributeTemplate, form=form)

@admin.route('/attributeTemplates/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_attributeTemplate(id):
	# check_admin()

	attributeTemplate = AttributeTemplate.query.get_or_404(id)
	db.session.delete(attributeTemplate)
	db.session.commit()
	flash('You have successfully deleted the attribute template.')

	return redirect(url_for('admin.list_attributeTemplates'))

@admin.route('/attributeTemplates/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_attributeTemplate(id):
	# check_admin()

	add_attributeTemplate = False

	attributeTemplate = AttributeTemplate.query.get_or_404(id)
	form = AttributeTemplateForm(obj=attributeTemplate)

	# Edit an existing attributeTemplate.
	if form.validate_on_submit():
		attributeTemplate.ElementTemplate = form.elementTemplate.data
		attributeTemplate.Name = form.name.data
		attributeTemplate.Description = form.description.data

		db.session.commit()

		flash('You have successfully edited the attributeTemplate.')

		return redirect(url_for('admin.list_attributeTemplates'))

	# Present a form to edit an existing attributeTemplate.
	form.elementTemplate.data = attributeTemplate.ElementTemplate
	form.name.data = attributeTemplate.Name
	form.description.data = attributeTemplate.Description
	return render_template('admin/attributeTemplates/attributeTemplate.html', add_attributeTemplate=add_attributeTemplate, form=form, attributeTemplate=attributeTemplate)

################################################################################
# Element views.
################################################################################

@admin.route('/elements', methods=['GET', 'POST'])
# @login_required
def list_elements():
	# check_admin()

	elements = Element.query.join(ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Element.Name)

	return render_template('admin/elements/elements.html', elements=elements)

@admin.route('/elements/add', methods=['GET', 'POST'])
# @login_required
def add_element():
	# check_admin()

	add_element = True

	form = ElementForm()

	# Add a new element.
	if form.validate_on_submit():
		element = Element(ElementTemplate=form.elementTemplate.data, Name=form.name.data, Description=form.description.data)
		db.session.add(element)
		db.session.commit()
		flash('You have successfully added a new element.')

		return redirect(url_for('admin.list_elements'))

	# Present a form to add a new element.
	return render_template('admin/elements/element.html', add_element=add_element, form=form)

@admin.route('/elements/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_element(id):
	# check_admin()

	element = Element.query.get_or_404(id)
	db.session.delete(element)
	db.session.commit()
	flash('You have successfully deleted the element.')

	return redirect(url_for('admin.list_elements'))

@admin.route('/elements/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_element(id):
	# check_admin()

	add_element = False

	element = Element.query.get_or_404(id)
	form = ElementForm(obj=element)

	# Edit an existing element.
	if form.validate_on_submit():
		element.ElementTemplate = form.elementTemplate.data
		element.Name = form.name.data
		element.Description = form.description.data

		db.session.commit()

		flash('You have successfully edited the element.')

		return redirect(url_for('admin.list_elements'))

	# Present a form to edit an existing element.
	form.elementTemplate.data = element.ElementTemplate
	form.name.data = element.Name
	form.description.data = element.Description
	return render_template('admin/elements/element.html', add_element=add_element, form=form, element=element)

################################################################################
# Element Attribute views.
################################################################################
@admin.route('/elementAttributes', methods=['GET', 'POST'])
# @login_required
def list_elementAttributes():
	# check_admin()

	elementAttributes = ElementAttribute.query.join(Element, Tag, ElementTemplate, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, Tag.Name)

	return render_template('admin/elementAttributes/elementAttributes.html', elementAttributes=elementAttributes)

@admin.route('/elementAttributes/add', methods=['GET', 'POST'])
# @login_required
def add_elementAttribute():
	# check_admin()

	add_elementAttribute = True

	form = ElementAttributeForm()

	# Add a new element attribute.
	if form.validate_on_submit():
		elementAttribute = ElementAttribute(Element=form.element.data, AttributeTemplate=form.attributeTemplate.data, Tag=form.tag.data)
		db.session.add(elementAttribute)
		db.session.commit()
		flash('You have successfully added a new elementAttribute.')

		return redirect(url_for('admin.list_elementAttributes'))

	# Present a form to add a new element attribute.
	return render_template('admin/elementAttributes/elementAttribute.html', add_elementAttribute=add_elementAttribute, form=form)

@admin.route('/elementAttributes/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_elementAttribute(id):
	# check_admin()

	elementAttribute = ElementAttribute.query.get_or_404(id)
	db.session.delete(elementAttribute)
	db.session.commit()
	flash('You have successfully deleted the elementAttribute.')

	return redirect(url_for('admin.list_elementAttributes'))

@admin.route('/elementAttributes/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_elementAttribute(id):
	# check_admin()

	add_elementAttribute = False

	elementAttribute = ElementAttribute.query.get_or_404(id)
	form = ElementAttributeForm(obj=elementAttribute)

	# Edit an existing element attribute.
	if form.validate_on_submit():	
		elementAttribute.Element = form.element.data
		elementAttribute.AttributeTemplate = form.attributeTemplate.data
		elementAttribute.Tag = form.tag.data

		db.session.commit()

		flash('You have successfully edited the element attribute.')

		return redirect(url_for('admin.list_elementAttributes'))

	# Present a form to edit an existing element attribute.
	form.element.data = elementAttribute.Element
	form.attributeTemplate.data = elementAttribute.AttributeTemplate
	form.tag.data = elementAttribute.Tag
	return render_template('admin/elementAttributes/elementAttribute.html', add_elementAttribute=add_elementAttribute, form=form, elementAttribute=elementAttribute)

################################################################################
# Element Template views.
################################################################################

@admin.route('/elementTemplates', methods=['GET', 'POST'])
# @login_required
def list_elementTemplates():
	# check_admin()

	elementTemplates = ElementTemplate.query.join(Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name)

	return render_template('admin/elementTemplates/elementTemplates.html', elementTemplates=elementTemplates)

@admin.route('/elementTemplates/add', methods=['GET', 'POST'])
# @login_required
def add_elementTemplate():
	# check_admin()

	add_elementTemplate = True

	form = ElementTemplateForm()

	# Add a new elementTemplate.
	if form.validate_on_submit():
		elementTemplate = ElementTemplate(Site=form.site.data, Name=form.name.data, Description=form.description.data)
		db.session.add(elementTemplate)
		db.session.commit()
		flash('You have successfully added a new element template.')

		return redirect(url_for('admin.list_elementTemplates'))

	# Present a form to add a new element template.
	return render_template('admin/elementTemplates/elementTemplate.html', add_elementTemplate=add_elementTemplate, form=form)

@admin.route('/elementTemplates/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_elementTemplate(id):
	# check_admin()

	elementTemplate = ElementTemplate.query.get_or_404(id)
	db.session.delete(elementTemplate)
	db.session.commit()
	flash('You have successfully deleted the element template.')

	return redirect(url_for('admin.list_elementTemplates'))

@admin.route('/elementTemplates/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_elementTemplate(id):
	# check_admin()

	add_elementTemplate = False

	elementTemplate = ElementTemplate.query.get_or_404(id)
	form = ElementTemplateForm(obj=elementTemplate)

	# Edit an existing element template.
	if form.validate_on_submit():
		elementTemplate.Site = form.site.data
		elementTemplate.Name = form.name.data
		elementTemplate.Description = form.description.data

		db.session.commit()

		flash('You have successfully edited the element template.')

		return redirect(url_for('admin.list_elementTemplates'))

	# Present a form to edit an existing element template.
	form.site.data = elementTemplate.Site
	form.name.data = elementTemplate.Name
	form.description.data = elementTemplate.Description
	return render_template('admin/elementTemplates/elementTemplate.html', add_elementTemplate=add_elementTemplate, form=form, elementTemplate=elementTemplate)

################################################################################
# Enterprise views.
################################################################################

@admin.route('/enterprises', methods=['GET', 'POST'])
# @login_required
def list_enterprises():
	# check_admin()

	enterprises = Enterprise.query.order_by(Enterprise.Name)

	return render_template('admin/enterprises/enterprises.html', enterprises=enterprises)

@admin.route('/enterprises/add', methods=['GET', 'POST'])
# @login_required
def add_enterprise():
	# check_admin()

	add_enterprise = True

	form = EnterpriseForm()

	# Add a new enterprise.
	if form.validate_on_submit():
		enterprise = Enterprise(Name=form.name.data, Abbreviation=form.abbreviation.data, Description=form.description.data)
		db.session.add(enterprise)
		db.session.commit()
		flash('You have successfully added a new enterprise.')

		return redirect(url_for('admin.list_enterprises'))

	# Present a form to add a new enterprise.
	return render_template('admin/enterprises/enterprise.html', add_enterprise=add_enterprise, form=form)

@admin.route('/enterprises/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_enterprise(id):
	# check_admin()

	enterprise = Enterprise.query.get_or_404(id)
	db.session.delete(enterprise)
	db.session.commit()
	flash('You have successfully deleted the enterprise.')

	return redirect(url_for('admin.list_enterprises'))

@admin.route('/enterprises/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_enterprise(id):
	# check_admin()

	add_enterprise = False

	enterprise = Enterprise.query.get_or_404(id)
	form = EnterpriseForm(obj=enterprise)

	# Edit an existing enterprise.
	if form.validate_on_submit():
		enterprise.Name = form.name.data
		enterprise.Abbreviation = form.abbreviation.data
		enterprise.Description = form.description.data

		db.session.commit()

		flash('You have successfully edited the enterprise.')

		return redirect(url_for('admin.list_enterprises'))

	# Present a form to edit an existing enterprise.
	form.name.data = enterprise.Name
	form.abbreviation.data = enterprise.Abbreviation
	form.description.data = enterprise.Description
	return render_template('admin/enterprises/enterprise.html', add_enterprise=add_enterprise, form=form, enterprise=enterprise)

################################################################################
# Event Frame views.
################################################################################

@admin.route('/eventFrames', methods=['GET', 'POST'])
# @login_required
def list_eventFrames():
	# check_admin()

	eventFrames = EventFrame.query.join(EventFrameTemplate, ElementTemplate, Site, Enterprise)\
		.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name, EventFrame.Name)

	return render_template('admin/eventFrames/eventFrames.html', eventFrames=eventFrames)

@admin.route('/eventFrames/add', methods=['GET', 'POST'])
# @login_required
def add_eventFrame():
	# check_admin()

	add_eventFrame = True

	form = EventFrameForm()

	# Add a new event frame.
	if form.validate_on_submit():
		eventFrame = EventFrame(EventFrameTemplate=form.eventFrameTemplate.data, Name=form.name.data, Description=form.description.data, \
			ParentEventFrame=form.parentEventFrame.data, Order=form.order.data, StartTime=form.startTime.data, EndTime=form.endTime.data)
		db.session.add(eventFrame)
		db.session.commit()
		flash("You have successfully added a new Event Frame.")

		return redirect(url_for('admin.list_eventFrames'))

	# Present a form to add a new event frame.
	return render_template('admin/eventFrames/eventFrame.html', add_eventFrame=add_eventFrame, form=form)

@admin.route('/eventFrames/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_eventFrame(id):
	# check_admin()

	eventFrame = EventFrame.query.get_or_404(id)
	db.session.delete(eventFrame)
	db.session.commit()
	flash('You have successfully deleted the event frame.')

	return redirect(url_for('admin.list_eventFrames'))

@admin.route('/eventFrames/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_eventFrame(id):
	# check_admin()

	add_eventFrame = False

	eventFrame = EventFrame.query.get_or_404(id)
	form = EventFrameForm(obj=eventFrame)

	# Edit an existing event frame.
	if form.validate_on_submit():
		eventFrame.EventFrameTemplate = form.eventFrameTemplate.data
		eventFrame.Name = form.name.data
		eventFrame.Description = form.description.data
		eventFrame.ParentEventFrame = form.parentEventFrame.data
		eventFrame.Order = form.order.data
		eventFrame.StartTime = form.startTime.data
		eventFrame.EndTime = form.endTime.data
		db.session.commit()
		flash('You have successfully edited the Event Frame.')

		return redirect(url_for('admin.list_eventFrames'))

	# Present a form to edit an existing event frame template.
	form.eventFrameTemplate.data = eventFrame.EventFrameTemplate
	form.name.data = eventFrame.Name
	form.description.data = eventFrame.Description
	form.parentEventFrame.data = eventFrame.ParentEventFrame
	form.order.data = eventFrame.Order
	form.startTime.data = eventFrame.StartTime
	form.endTime.data = eventFrame.EndTime

	return render_template('admin/eventFrames/eventFrame.html', add_eventFrame=add_eventFrame, form=form, eventFrame=eventFrame)

################################################################################
# Event Frame Template views.
################################################################################

@admin.route('/eventFrameTemplates', methods=['GET', 'POST'])
# @login_required
def list_eventFrameTemplates():
	# check_admin()

	eventFrameTemplates = EventFrameTemplate.query.join(ElementTemplate, Site, Enterprise)\
							.order_by(Enterprise.Abbreviation, Site.Abbreviation, ElementTemplate.Name, EventFrameTemplate.Name)

	return render_template('admin/eventFrameTemplates/eventFrameTemplates.html', eventFrameTemplates=eventFrameTemplates)

@admin.route('/eventFrameTemplates/add', methods=['GET', 'POST'])
# @login_required
def add_eventFrameTemplate():
	# check_admin()

	add_eventFrameTemplate = True

	form = EventFrameTemplateForm()

	# Add a new event frame template.
	if form.validate_on_submit():
		eventFrameTemplate = EventFrameTemplate(ElementTemplate=form.elementTemplate.data, Name=form.name.data, Description=form.description.data, \
			ParentEventFrameTemplate=form.parentEventFrameTemplate.data)
		if eventFrameTemplate.ParentEventFrameTemplate is not None and \
		eventFrameTemplate.ParentEventFrameTemplate.ElementTemplateId != eventFrameTemplate.ElementTemplateId:
			flash("Unable to add new Event Frame Template due to conflicting Element Template with Parent Event Frame.")
		else:
			db.session.add(eventFrameTemplate)
			db.session.commit()
			flash("You have successfully added a new event frame template.")

		return redirect(url_for('admin.list_eventFrameTemplates'))

	# Present a form to add a new event frame template.
	return render_template('admin/eventFrameTemplates/eventFrameTemplate.html', add_eventFrameTemplate=add_eventFrameTemplate, form=form)

@admin.route('/eventFrameTemplates/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_eventFrameTemplate(id):
	# check_admin()

	eventFrameTemplate = EventFrameTemplate.query.get_or_404(id)
	db.session.delete(eventFrameTemplate)
	db.session.commit()
	flash('You have successfully deleted the event frame template.')

	return redirect(url_for('admin.list_eventFrameTemplates'))

@admin.route('/eventFrameTemplates/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_eventFrameTemplate(id):
	# check_admin()

	add_eventFrameTemplate = False

	eventFrameTemplate = EventFrameTemplate.query.get_or_404(id)
	form = EventFrameTemplateForm(obj=eventFrameTemplate)

	# Edit an existing event frame template.
	if form.validate_on_submit():
		eventFrameTemplate.ElementTemplate = form.elementTemplate.data
		eventFrameTemplate.Name = form.name.data
		eventFrameTemplate.Description = form.description.data
		eventFrameTemplate.ParentEventFrameTemplate = form.parentEventFrameTemplate.data
		if eventFrameTemplate.ParentEventFrameTemplate is not None and \
		eventFrameTemplate.ParentEventFrameTemplate.ElementTemplateId != eventFrameTemplate.ElementTemplateId:
			flash("Unable to save Event Frame Template due to conflicting Element Template with Parent Event Frame Template.")
		else:
			db.session.commit()
			flash('You have successfully edited the event frame template.')

		return redirect(url_for('admin.list_eventFrameTemplates'))

	# Present a form to edit an existing event frame template.
	form.elementTemplate.data = eventFrameTemplate.ElementTemplate
	form.name.data = eventFrameTemplate.Name
	form.description.data = eventFrameTemplate.Description
	form.parentEventFrameTemplate.data = eventFrameTemplate.ParentEventFrameTemplate

	return render_template('admin/eventFrameTemplates/eventFrameTemplate.html', add_eventFrameTemplate=add_eventFrameTemplate, form=form, \
		eventFrameTemplate=eventFrameTemplate)

################################################################################
# Lookup views.
################################################################################

@admin.route('/lookups', methods=['GET', 'POST'])
# @login_required
def list_lookups():
	# check_admin()

	lookups = Lookup.query.join(Enterprise).order_by(Enterprise.Abbreviation, Lookup.Name)

	return render_template('admin/lookups/lookups.html', lookups=lookups, title="Lookups")

@admin.route('/lookups/add', methods=['GET', 'POST'])
# @login_required
def add_lookup():
	# check_admin()

	add_lookup = True

	form = LookupForm()

	# Add a new lookup.
	if form.validate_on_submit():
		lookup = Lookup(Enterprise=form.enterprise.data, Name=form.name.data)
		db.session.add(lookup)
		db.session.commit()
		flash('You have successfully added a new lookup.')

		return redirect(url_for('admin.list_lookups'))

	# Present a form to add a new lookup.
	return render_template('admin/lookups/lookup.html', add_lookup=add_lookup, form=form)

@admin.route('/lookups/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_lookup(id):
	# check_admin()

	lookup = Lookup.query.get_or_404(id)
	db.session.delete(lookup)
	db.session.commit()
	flash('You have successfully deleted the lookup.')

	return redirect(url_for('admin.list_lookups'))

@admin.route('/lookups/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_lookup(id):
	# check_admin()

	add_lookup = False

	lookup = Lookup.query.get_or_404(id)
	form = LookupForm(obj=lookup)

	# Edit an existing lookup.
	if form.validate_on_submit():
		lookup.Enterprise = form.enterprise.data
		lookup.Name = form.name.data

		db.session.commit()

		flash('You have successfully edited the lookup.')

		return redirect(url_for('admin.list_lookups'))

	# Present a form to edit an existing lookup.
	form.enterprise.data = lookup.Enterprise
	form.name.data = lookup.Name
	return render_template('admin/lookups/lookup.html', add_lookup=add_lookup, form=form, lookup=lookup)

################################################################################
# Lookup Value views.
################################################################################

@admin.route('/lookupValues', methods=['GET', 'POST'])
# @login_required
def list_lookupValues():
	# check_admin()

	lookupValues = LookupValue.query.join(Lookup, Enterprise).order_by(Enterprise.Abbreviation, Lookup.Name, LookupValue.Name)

	return render_template('admin/lookupValues/lookupValues.html', lookupValues=lookupValues)

@admin.route('/lookupValues/add', methods=['GET', 'POST'])
# @login_required
def add_lookupValue():
	# check_admin()

	add_lookupValue = True

	form = LookupValueForm()

	# Add a new lookupValue.
	if form.validate_on_submit():
		lookupValue = LookupValue(Lookup=form.lookup.data, Name=form.name.data)
		db.session.add(lookupValue)
		db.session.commit()
		flash('You have successfully added a new lookup value.')

		return redirect(url_for('admin.list_lookupValues'))

	# Present a form to add a new lookupValue.
	return render_template('admin/lookupValues/lookupValue.html', add_lookupValue=add_lookupValue, form=form)

@admin.route('/lookupValues/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_lookupValue(id):
	# check_admin()

	lookupValue = LookupValue.query.get_or_404(id)
	db.session.delete(lookupValue)
	db.session.commit()
	flash('You have successfully deleted the lookup value.')

	return redirect(url_for('admin.list_lookupValues'))

@admin.route('/lookupValues/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_lookupValue(id):
	# check_admin()

	add_lookupValue = False

	lookupValue = LookupValue.query.get_or_404(id)
	form = LookupValueForm(obj=lookupValue)

	# Edit an existing lookupValue.
	if form.validate_on_submit():
		lookupValue.Lookup = form.lookup.data
		lookupValue.Name = form.name.data

		db.session.commit()

		flash('You have successfully edited the lookup value.')

		return redirect(url_for('admin.list_lookupValues'))

	# Present a form to edit an existing lookupValue.
	form.lookup.data = lookupValue.Lookup
	form.name.data = lookupValue.Name
	return render_template('admin/lookupValues/lookupValue.html', add_lookupValue=add_lookupValue, form=form, lookupValue=lookupValue)

################################################################################
# Site views.
################################################################################

@admin.route('/sites', methods=['GET', 'POST'])
# @login_required
def list_sites():
	# check_admin()

	sites = Site.query.join(Enterprise).order_by(Enterprise.Abbreviation, Site.Name)

	return render_template('admin/sites/sites.html', sites=sites, title="Sites")

@admin.route('/sites/add', methods=['GET', 'POST'])
# @login_required
def add_site():
	# check_admin()

	add_site = True

	form = SiteForm()

	# Add a new site.
	if form.validate_on_submit():
		site = Site(Enterprise=form.enterprise.data, Name=form.name.data, Abbreviation=form.abbreviation.data, Description=form.description.data)
		db.session.add(site)
		db.session.commit()
		flash('You have successfully added a new site.')

		return redirect(url_for('admin.list_sites'))

	# Present a form to add a new site.
	return render_template('admin/sites/site.html', add_site=add_site, form=form)

@admin.route('/sites/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_site(id):
	# check_admin()

	site = Site.query.get_or_404(id)
	db.session.delete(site)
	db.session.commit()
	flash('You have successfully deleted the site.')

	return redirect(url_for('admin.list_sites'))

@admin.route('/sites/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_site(id):
	# check_admin()

	add_site = False

	site = Site.query.get_or_404(id)
	form = SiteForm(obj=site)

	# Edit an existing site.
	if form.validate_on_submit():
		site.Enterprise = form.enterprise.data
		site.Name = form.name.data
		site.Abbreviation = form.abbreviation.data
		site.Description = form.description.data

		db.session.commit()

		flash('You have successfully edited the site.')

		return redirect(url_for('admin.list_sites'))

	# Present a form to edit an existing site.
	form.enterprise.data = site.Enterprise
	form.name.data = site.Name
	form.abbreviation.data = site.Abbreviation
	form.description.data = site.Description
	return render_template('admin/sites/site.html', add_site=add_site, form=form, site=site)

################################################################################
# Tag views.
################################################################################

@admin.route('/tags', methods=['GET', 'POST'])
# @login_required
def list_tags():
	# check_admin()

	tags = Tag.query.join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name)

	return render_template('admin/tags/tags.html', tags=tags)

@admin.route('/tags/add', methods=['GET', 'POST'])
# @login_required
def add_tag():
	# check_admin()

	add_tag = True

	form = TagForm()

	# Add a new tag.
	if form.validate_on_submit():
		tag = Tag(Area=form.area.data, Name=form.name.data, Description=form.description.data, UnitOfMeasurement=form.unitOfMeasurement.data)
		db.session.add(tag)
		db.session.commit()
		flash('You have successfully added a new tag.')

		return redirect(url_for('admin.list_tags'))

	# Present a form to add a new tag.
	return render_template('admin/tags/tag.html', add_tag=add_tag, form=form)

@admin.route('/tags/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_tag(id):
	# check_admin()

	tag = Tag.query.get_or_404(id)
	db.session.delete(tag)
	db.session.commit()
	flash('You have successfully deleted the tag.')

	return redirect(url_for('admin.list_tags'))

@admin.route('/tags/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_tag(id):
	# check_admin()

	add_tag = False

	tag = Tag.query.get_or_404(id)
	form = TagForm(obj=tag)

	# Edit an existing tag.
	if form.validate_on_submit():
		tag.Area = form.area.data
		tag.Name = form.name.data
		tag.Description = form.description.data
		tag.UnitOfMeasurement = form.unitOfMeasurement.data

		db.session.commit()

		flash('You have successfully edited the tag.')

		return redirect(url_for('admin.list_tags'))

	# Present a form to edit an existing tag.
	form.area.data = tag.Area
	form.name.data = tag.Name
	form.description.data = tag.Description
	form.unitOfMeasurement.data = tag.UnitOfMeasurement
	return render_template('admin/tags/tag.html', add_tag=add_tag, form=form, tag=tag)

################################################################################
# Tag Value views.
################################################################################

@admin.route('/tagValues/<int:tagId>', methods=['GET', 'POST'])
# @login_required
def list_tagValues(tagId):
	# check_admin()

	tag = Tag.query.get_or_404(tagId)

	page = request.args.get('page', 1, type=int)
	pagination = TagValue.query.join(Tag).filter_by(TagId=tag.TagId).join(Area, Site, Enterprise).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name, TagValue.Timestamp.desc()).paginate(page, per_page=10, error_out=False)
	tagValues = pagination.items

	return render_template('admin/tagValues/tagValues.html', tagId=tagId, tagValues=tagValues, pagination=pagination)

# @admin.route('/tagValues/add', methods=['GET', 'POST'])
# # @login_required
# def add_tagValue():
# 	# check_admin()

# 	add_tagValue = True

# 	form = TagValueForm()

# 	# Add a new tag value.
# 	if form.validate_on_submit():
# 		tagValue = TagValue(Tag=form.tag.data, Timestamp=form.timestamp.data, Value=form.value.data)
# 		db.session.add(tagValue)
# 		db.session.commit()
# 		flash('You have successfully added a new tag value.')

# 		return redirect(url_for('admin.list_tagValues'))

# 	# Present a form to add a new tag value.
# 	return render_template('admin/tagValues/tagValue.html', add_tagValue=add_tagValue, form=form)

@admin.route('/tagValues/add/<int:tagId>', methods=['GET', 'POST'])
# @login_required
def add_tagValue(tagId):
	# check_admin()

	add_tagValue = True

	tag = Tag.query.get_or_404(tagId)
	form = TagValueForm()

	# Add a new tag value.
	if form.validate_on_submit():
		tagValue = TagValue(Tag=tag, Timestamp=form.timestamp.data, Value=form.value.data)
		db.session.add(tagValue)
		db.session.commit()
		flash('You have successfully added a new tag value.')

		return redirect(url_for('admin.list_tagValues', tagId=tag.TagId))

	# Present a form to add a new tag value.
	form.tag.data = tag
	return render_template('admin/tagValues/tagValue.html', add_tagValue=add_tagValue, form=form)

@admin.route('/tagValues/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_tagValue(id):
	# check_admin()

	tagValue = TagValue.query.get_or_404(id)
	db.session.delete(tagValue)
	db.session.commit()
	flash('You have successfully deleted the tag value.')

	return redirect(url_for('admin.list_tagValues', tagId=tagValue.TagId))

@admin.route('/tagValues/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_tagValue(id):
	# check_admin()

	add_tagValue = False

	tagValue = TagValue.query.get_or_404(id)
	form = TagValueForm(obj=tagValue)

	# Edit an existing tagValue.
	if form.validate_on_submit():
		tagValue.Tag = form.tag.data
		tagValue.Timestamp = form.timestamp.data
		tagValue.Value = form.value.data

		db.session.commit()

		flash('You have successfully edited the tag value.')

		return redirect(url_for('admin.list_tagValues', tagId=tagValue.TagId))

	# Present a form to edit an existing tagValue.
	form.tag.data = tagValue.Tag
	form.timestamp.data = tagValue.Timestamp
	form.value.data = tagValue.Value
	return render_template('admin/tagValues/tagValue.html', add_tagValue=add_tagValue, form=form, tagValue=tagValue)

################################################################################
# Unit of Measurement views.
################################################################################

@admin.route('/unitsOfMeasurement', methods=['GET', 'POST'])
# @login_required
def list_unitsOfMeasurement():
	# check_admin()

	page = request.args.get('page', 1, type=int)
	pagination = UnitOfMeasurement.query.order_by(UnitOfMeasurement.Name).paginate(page, per_page=10, error_out=False)
	unitsOfMeasurement = pagination.items

	return render_template('admin/unitsOfMeasurement/unitsOfMeasurement.html', unitsOfMeasurement=unitsOfMeasurement, pagination=pagination)

@admin.route('/units/add', methods=['GET', 'POST'])
# @login_required
def add_unitOfMeasurement():
	# check_admin()

	add_unitOfMeasurement = True

	form = UnitOfMeasurementForm()

	# Add a new unit of measurement.
	if form.validate_on_submit():
		unitOfMeasurement = UnitOfMeasurement(Name=form.name.data, Abbreviation=form.abbreviation.data)
		db.session.add(unitOfMeasurement)
		db.session.commit()
		flash('You have successfully added a new unit of measurement.')

		return redirect(url_for('admin.list_unitsOfMeasurement'))

	# Present a form to add a new unit of measurement.
	return render_template('admin/unitsOfMeasurement/unitOfMeasurement.html', add_unitOfMeasurement=add_unitOfMeasurement, form=form)

@admin.route('/unitsOfMeasurement/delete/<int:id>', methods=['GET', 'POST'])
# @login_required
def delete_unitOfMeasurement(id):
	# check_admin()

	unitOfMeasurement = UnitOfMeasurement.query.get_or_404(id)
	db.session.delete(unitOfMeasurement)
	db.session.commit()
	flash('You have successfully deleted the unit of measurement.')

	return redirect(url_for('admin.list_unitsOfMeasurement'))

@admin.route('/unitsOfMeasurement/edit/<int:id>', methods=['GET', 'POST'])
# @login_required
def edit_unitOfMeasurement(id):
	# check_admin()

	add_unitOfMeasurement = False

	unitOfMeasurement = UnitOfMeasurement.query.get_or_404(id)
	form = UnitOfMeasurementForm(obj=unitOfMeasurement)

	# Edit an existing unit of measurement.
	if form.validate_on_submit():
		unitOfMeasurement.Name = form.name.data
		unitOfMeasurement.Abbreviation = form.abbreviation.data

		db.session.commit()

		flash('You have successfully edited the unit of measurement.')

		return redirect(url_for('admin.list_unitsOfMeasurement'))

	# Present a form to edit an existing unit of measurement.
	form.name.data = unitOfMeasurement.Name
	form.abbreviation.data = unitOfMeasurement.Abbreviation
	return render_template('admin/unitsOfMeasurement/unitOfMeasurement.html', add_unitOfMeasurement=add_unitOfMeasurement, form=form, unitOfMeasurement=unitOfMeasurement)
