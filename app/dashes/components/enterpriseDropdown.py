import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import Enterprise

def layout():
    return dcc.Dropdown(id = "enterpriseDropdown", placeholder = "Select Enterprise", multi = False, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def enterpriseDropdownOptions(urlHref):
        return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

def valueCallback(dashApp):
    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "value"),
        [Input(component_id = "enterpriseDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "enterpriseDropdown", component_property = "value")])
    def enterpriseDropdownValue(enterpriseDropdownOptions, urlHref, enterpriseDropdownValue):
        enterpriseId = None
        if enterpriseDropdownValue == -1:
            if enterpriseDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "enterpriseId" in queryString:
                    id = int(queryString["enterpriseId"][0])                
                    if len(list(filter(lambda enterprise: enterprise["value"] == id, enterpriseDropdownOptions))) > 0:
                        enterpriseId = id

        return enterpriseId
