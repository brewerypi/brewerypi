from dash import dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import ElementTemplate

def layout():
    return dcc.Dropdown(id = "elementTemplatesDropdown", placeholder = "Select Element Template(s)", multi = True, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "elementTemplatesDropdown", component_property = "options"),
        [Input(component_id = "siteDropdown", component_property = "value")])
    def elementTemplatesDropdownOptions(siteDropdownValue):
        return [{"label": elementTemplate.Name, "value": elementTemplate.ElementTemplateId} for elementTemplate in ElementTemplate.query. \
            filter(ElementTemplate.SiteId == siteDropdownValue).order_by(ElementTemplate.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "elementTemplatesDropdown", component_property = "value"),
        [Input(component_id = "elementTemplatesDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "elementTemplatesDropdown", component_property = "value")])
    def elementTemplatesDropdownValues(elementTemplatesDropdownOptions, urlHref, elementTemplatesDropdownValues):
        elementTemplateIds = []
        if elementTemplatesDropdownValues == -1:
            if elementTemplatesDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "elementTemplateId" in queryString:
                    for elementTemplateId in map(int, queryString["elementTemplateId"]):
                        if len(list(filter(lambda elementTemplate: elementTemplate["value"] == elementTemplateId, elementTemplatesDropdownOptions))) > 0:
                            elementTemplateIds.append(elementTemplateId)
        else:
            if elementTemplatesDropdownOptions and elementTemplatesDropdownValues:
                for elementTemplateId in elementTemplatesDropdownValues:
                    if len(list(filter(lambda elementTemplate: elementTemplate["value"] == elementTemplateId, elementTemplatesDropdownOptions))) > 0:
                        elementTemplateIds.append(elementTemplateId)

        return elementTemplateIds
