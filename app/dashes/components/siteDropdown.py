import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
from urllib.parse import parse_qs, urlparse
from app.models import Enterprise, Site

def layout():
    return dcc.Dropdown(id = "siteDropdown", placeholder = "Select Site", multi = False)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "options"),
        [Input(component_id = "enterpriseDropdown", component_property = "value")])
    def sitesDropdownOptions(enterpriseDropdownValue):
        return [{"label": "{}_{}".format(site.Enterprise.Abbreviation, site.Name), "value": site.SiteId} for site in 
            Site.query.join(Enterprise).filter(Site.EnterpriseId == enterpriseDropdownValue).order_by(Enterprise.Abbreviation, Site.Name).all()]

def valueCallback(dashApp):
    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "value"),
        [Input(component_id = "siteDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
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
