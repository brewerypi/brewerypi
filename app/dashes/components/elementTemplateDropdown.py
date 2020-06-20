import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import ElementTemplate

def layout():
    return dcc.Dropdown(id = "elementTemplateDropdown", placeholder = "Select Element Template", multi = False, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "elementTemplateDropdown", component_property = "options"),
        [Input(component_id = "siteDropdown", component_property = "value")])
    def elementTemplateDropdownOptions(siteDropdownValue):
        return [{"label": elementTemplate.Name, "value": elementTemplate.ElementTemplateId} for elementTemplate in ElementTemplate.query. \
            filter(ElementTemplate.SiteId == siteDropdownValue).order_by(ElementTemplate.Name).all()]

def valueCallback(dashApp):
    @dashApp.callback(Output(component_id = "elementTemplateDropdown", component_property = "value"),
        [Input(component_id = "elementTemplateDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "elementTemplateDropdown", component_property = "value")])
    def elementTemplateDropdownValue(elementTemplateDropdownOptions, urlHref, elementTemplateDropdownValue):
        elementTemplateId = None
        if elementTemplateDropdownValue == -1:
            if elementTemplateDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "elementTemplateId" in queryString:
                    id = int(queryString["elementTemplateId"][0])                
                    if len(list(filter(lambda elementTemplate: elementTemplate["value"] == id, elementTemplateDropdownOptions))) > 0:
                        elementTemplateId = id

        return elementTemplateId
