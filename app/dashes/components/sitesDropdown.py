import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import Enterprise, Site

def layout():
    return dcc.Dropdown(id = "sitesDropdown", placeholder = "Select Site(s)", multi = True)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "sitesDropdown", component_property = "options"),
        [Input(component_id = "enterprisesDropdown", component_property = "value")])
    def sitesDropdownOptions(enterprisesDropdownValues):
        return [{"label": "{}_{}".format(site.Enterprise.Abbreviation, site.Name), "value": site.SiteId} for site in 
            Site.query.join(Enterprise).filter(Site.EnterpriseId.in_(enterprisesDropdownValues)).order_by(Enterprise.Abbreviation, Site.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "sitesDropdown", component_property = "value"),
        [Input(component_id = "sitesDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "sitesDropdown", component_property = "value")])
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
            if sitesDropdownOptions and sitesDropdownValues:
                for siteId in sitesDropdownValues:
                    if len(list(filter(lambda site: site["value"] == siteId, sitesDropdownOptions))) > 0:
                        siteIds.append(siteId)

        return siteIds
