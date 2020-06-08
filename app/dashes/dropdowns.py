import dash
import dash_core_components as dcc
from urllib.parse import parse_qs, urlparse
from app.models import Area, ElementTemplate, Enterprise, EventFrameTemplate, Site, Tag

def areasDropdownOptions(siteIds):
    return [{"label": "{}_{}_{}".format(area.Site.Enterprise.Abbreviation, area.Site.Abbreviation, area.Name), "value": area.AreaId} for area in 
        Area.query.join(Site, Enterprise).filter(Area.SiteId.in_(siteIds)).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Name).all()]

def areasDropdownValues(areasDropdownOptions, urlHref, areasDropdownValues):
    areaIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if areasDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "areaId" in queryString:
                for areaId in map(int, queryString["areaId"]):
                    if len(list(filter(lambda area: area["value"] == areaId, areasDropdownOptions))) > 0:
                        areaIds.append(areaId)
    else:
        if areasDropdownOptions:
            for areaId in areasDropdownValues:
                if len(list(filter(lambda area: area["value"] == areaId, areasDropdownOptions))) > 0:
                    areaIds.append(areaId)

    return areaIds

def areasLayout():
    return dcc.Dropdown(id = "areasDropdown", placeholder = "Select Area(s)", multi = True)

def elementTemplateDropdownOptions(siteIds):
    return [{"label": elementTemplate.Name, "value": elementTemplate.ElementTemplateId} for elementTemplate in ElementTemplate.query. \
        filter(ElementTemplate.SiteId.in_(siteIds)).order_by(ElementTemplate.Name).all()]

def elementTemplateDropdownValue(elementTemplateDropdownOptions, urlHref):
    elementTemplateId = None
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if elementTemplateDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "elementTemplateId" in queryString:
                id = int(queryString["elementTemplateId"][0])                
                if len(list(filter(lambda elementTemplate: elementTemplate["value"] == id, elementTemplateDropdownOptions))) > 0:
                    elementTemplateId = id

    return elementTemplateId

def elementTemplateLayout():
    return dcc.Dropdown(id = "elementTemplateDropdown", placeholder = "Select Element Template", multi = False)

def enterpriseDropdownOptions(urlHref):
    return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

def enterprisesDropdownOptions(urlHref):
    return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

def enterpriseDropdownValue(enterpriseDropdownOptions, urlHref):
    enterpriseId = None
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if enterpriseDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "enterpriseId" in queryString:
                id = int(queryString["enterpriseId"][0])                
                if len(list(filter(lambda enterprise: enterprise["value"] == id, enterpriseDropdownOptions))) > 0:
                    enterpriseId = id

    return enterpriseId

def enterprisesDropdownValues(enterprisesDropdownOptions, urlHref):
    enterpriseIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if enterprisesDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "enterpriseId" in queryString:
                for enterpriseId in map(int, queryString["enterpriseId"]):
                    if len(list(filter(lambda enterprise: enterprise["value"] == enterpriseId, enterprisesDropdownOptions))) > 0:
                        enterpriseIds.append(enterpriseId)

    return enterpriseIds

def enterpriseLayout():
    return dcc.Dropdown(id = "enterpriseDropdown", placeholder = "Select Enterprise", multi = False)

def enterprisesLayout():
    return dcc.Dropdown(id = "enterprisesDropdown", placeholder = "Select Enterprise(s)", multi = True)

def eventFrameLayout():
    return dcc.Dropdown(id = "eventFrameDropdown", placeholder = "Select Event Frame", multi = False)

def eventFrameTemplateDropdownOptions(elementTemplateIds):
    return [{"label": eventFrameTemplate.Name, "value": eventFrameTemplate.EventFrameTemplateId} for eventFrameTemplate in EventFrameTemplate.query. \
        filter(EventFrameTemplate.ElementTemplateId.in_(elementTemplateIds)).order_by(EventFrameTemplate.Name).all()]

def eventFrameTemplateDropdownValue(eventFrameTemplateDropdownOptions, urlHref):
    eventFrameTemplateId = None
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if eventFrameTemplateDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "eventFrameTemplateId" in queryString:
                id = int(queryString["eventFrameTemplateId"][0])                
                if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == id, eventFrameTemplateDropdownOptions))) > 0:
                    eventFrameTemplateId = id

    return eventFrameTemplateId

def eventFrameTemplateLayout():
    return dcc.Dropdown(id = "eventFrameTemplateDropdown", placeholder = "Select Event Frame Template", multi = False)

def eventFrameTemplateViewLayout():
    return dcc.Dropdown(id = "eventFrameTemplateViewDropdown", placeholder = "Select View", multi = False)

def siteDropdownOptions(enterpriseIds):
    return [{"label": site.Name, "value": site.SiteId} for site in Site.query.filter(Site.EnterpriseId.in_(enterpriseIds)).order_by(Site.Name).all()]

def sitesDropdownOptions(enterpriseIds):
    return [{"label": "{}_{}".format(site.Enterprise.Abbreviation, site.Name), "value": site.SiteId} for site in 
        Site.query.join(Enterprise).filter(Site.EnterpriseId.in_(enterpriseIds)).order_by(Enterprise.Abbreviation, Site.Name).all()]

def siteDropdownValue(sitesDropdownOptions, urlHref):
    siteId = None
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if sitesDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "siteId" in queryString:
                id = int(queryString["siteId"][0])                
                if len(list(filter(lambda site: site["value"] == id, sitesDropdownOptions))) > 0:
                    siteId = id

    return siteId

def sitesDropdownValues(sitesDropdownOptions, urlHref, sitesDropdownValues):
    siteIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if sitesDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "siteId" in queryString:
                for siteId in map(int, queryString["siteId"]):
                    if len(list(filter(lambda site: site["value"] == siteId, sitesDropdownOptions))) > 0:
                        siteIds.append(siteId)
    else:
        if sitesDropdownOptions:
            for siteId in sitesDropdownValues:
                if len(list(filter(lambda site: site["value"] == siteId, sitesDropdownOptions))) > 0:
                    siteIds.append(siteId)

    return siteIds

def siteLayout():
    return dcc.Dropdown(id = "siteDropdown", placeholder = "Select Site", multi = False)

def sitesLayout():
    return dcc.Dropdown(id = "sitesDropdown", placeholder = "Select Site(s)", multi = True)

def tagsDropdownOptions(areaIds):
    return [{"label": "{}_{}_{}_{}".format(tag.Area.Site.Enterprise.Abbreviation, tag.Area.Site.Abbreviation, tag.Area.Abbreviation, tag.Name),
        "value": tag.TagId} for tag in Tag.query.join(Area, Site, Enterprise).filter(Tag.AreaId.in_(areaIds)).\
        order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name).all()]

def tagsDropdownValues(tagsDropdownOptions, urlHref, tagsDropdownValues):
    tagIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if tagsDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "tagId" in queryString:
                for tagId in map(int, queryString["tagId"]):
                    if len(list(filter(lambda tag: tag["value"] == tagId, tagsDropdownOptions))) > 0:
                        tagIds.append(tagId)
    else:
        if tagsDropdownOptions:
            for tagId in tagsDropdownValues:
                if len(list(filter(lambda tag: tag["value"] == tagId, tagsDropdownOptions))) > 0:
                    tagIds.append(tagId)

    return tagIds

def tagsLayout():
    return dcc.Dropdown(id = "tagsDropdown", placeholder = "Select Tag(s)", multi = True)
