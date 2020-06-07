import dash
import dash_core_components as dcc
from urllib.parse import parse_qs, urlparse
from app.models import Area, Enterprise, Site, Tag

def areaDropdownOptions(siteDropdownValues):
    return [{"label": "{}_{}_{}".format(area.Site.Enterprise.Abbreviation, area.Site.Abbreviation, area.Name), "value": area.AreaId} for area in 
        Area.query.join(Site, Enterprise).filter(Area.SiteId.in_(siteDropdownValues)). \
        order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Name).all()]

def areaDropdownValues(areaDropdownOptions, urlHref, areaDropdownValues):
    areaIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if areaDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "areaId" in queryString:
                for areaId in map(int, queryString["areaId"]):
                    if len(list(filter(lambda area: area["value"] == areaId, areaDropdownOptions))) > 0:
                        areaIds.append(areaId)
    else:
        if areaDropdownOptions:
            for areaId in areaDropdownValues:
                if len(list(filter(lambda area: area["value"] == areaId, areaDropdownOptions))) > 0:
                    areaIds.append(areaId)

    return areaIds

def areasLayout():
    return dcc.Dropdown(id = "areaDropdown", placeholder = "Select Area(s)", multi = True)

def enterpriseDropDownOptions(urlHref):
    return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

def enterpriseDropdownValues(enterpriseDropdownOptions, urlHref):
    enterpriseIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if enterpriseDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "enterpriseId" in queryString:
                for enterpriseId in map(int, queryString["enterpriseId"]):
                    if len(list(filter(lambda enterprise: enterprise["value"] == enterpriseId, enterpriseDropdownOptions))) > 0:
                        enterpriseIds.append(enterpriseId)

    return enterpriseIds

def enterprisesLayout():
    return dcc.Dropdown(id = "enterpriseDropdown", placeholder = "Select Enterprise(s)", multi = True)

def siteDropdownOptions(enterpriseDropdownValues):
    return [{"label": "{}_{}".format(site.Enterprise.Abbreviation, site.Name), "value": site.SiteId} for site in 
        Site.query.join(Enterprise).filter(Site.EnterpriseId.in_(enterpriseDropdownValues)).order_by(Enterprise.Abbreviation, Site.Name).all()]

def siteDropdownValues(siteDropdownOptions, urlHref, siteDropdownValues):
    siteIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if siteDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "siteId" in queryString:
                for siteId in map(int, queryString["siteId"]):
                    if len(list(filter(lambda site: site["value"] == siteId, siteDropdownOptions))) > 0:
                        siteIds.append(siteId)
    else:
        if siteDropdownOptions:
            for siteId in siteDropdownValues:
                if len(list(filter(lambda site: site["value"] == siteId, siteDropdownOptions))) > 0:
                    siteIds.append(siteId)

    return siteIds

def sitesLayout():
    return dcc.Dropdown(id = "siteDropdown", placeholder = "Select Site(s)", multi = True)

def tagDropdownOptions(areaDropdownValues):
    return [{"label": "{}_{}_{}_{}".format(tag.Area.Site.Enterprise.Abbreviation, tag.Area.Site.Abbreviation, tag.Area.Abbreviation, tag.Name),
        "value": tag.TagId} for tag in Tag.query.join(Area, Site, Enterprise).filter(Tag.AreaId.in_(areaDropdownValues)).\
        order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name).all()]

def tagDropdownValues(tagDropdownOptions, urlHref, tagDropdownValues):
    tagIds = []
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        if tagDropdownOptions:
            queryString = parse_qs(urlparse(urlHref).query)
            if "tagId" in queryString:
                for tagId in map(int, queryString["tagId"]):
                    if len(list(filter(lambda tag: tag["value"] == tagId, tagDropdownOptions))) > 0:
                        tagIds.append(tagId)
    else:
        if tagDropdownOptions:
            for tagId in tagDropdownValues:
                if len(list(filter(lambda tag: tag["value"] == tagId, tagDropdownOptions))) > 0:
                    tagIds.append(tagId)

    return tagIds

def tagsLayout():
    return dcc.Dropdown(id = "tagDropdown", placeholder = "Select Tag(s)", multi = True)
