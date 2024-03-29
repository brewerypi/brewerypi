import dash
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from urllib.parse import parse_qs, urlparse
from app.models import Enterprise

def layout():
    return dcc.Dropdown(id = "enterprisesDropdown", placeholder = "Select Enterprise(s)", multi = True, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "enterprisesDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def enterprisesDropdownOptions(urlHref):
        if dash.callback_context.triggered[0]["prop_id"] == ".":
            raise PreventUpdate

        return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "enterprisesDropdown", component_property = "value"),
        [Input(component_id = "enterprisesDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "enterprisesDropdown", component_property = "value")])
    def enterprisesDropdownValues(enterprisesDropdownOptions, urlHref, enterprisesDropdownValues):
        enterpriseIds = []
        if enterprisesDropdownValues == -1:
            if enterprisesDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "enterpriseId" in queryString:
                    for enterpriseId in map(int, queryString["enterpriseId"]):
                        if len(list(filter(lambda enterprise: enterprise["value"] == enterpriseId, enterprisesDropdownOptions))) > 0:
                            enterpriseIds.append(enterpriseId)

        return enterpriseIds
