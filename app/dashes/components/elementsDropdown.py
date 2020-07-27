import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import Element

def layout():
    return dcc.Dropdown(id = "elementsDropdown", placeholder = "Select Element(s)", multi = True, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "elementsDropdown", component_property = "options"),
        [Input(component_id = "elementTemplatesDropdown", component_property = "value")])
    def elementsDropdownOptions(elementTemplatesDropdownValues):
        return [{"label": "{} ({})".format(element.Name, element.ElementTemplate.Name), "value": element.ElementId} for element in Element.query. \
            filter(Element.ElementTemplateId.in_(elementTemplatesDropdownValues)).order_by(Element.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "elementsDropdown", component_property = "value"),
        [Input(component_id = "elementsDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "elementsDropdown", component_property = "value")])
    def elementsDropdownValues(elementsDropdownOptions, urlHref, elementsDropdownValues):
        elementIds = []
        if elementsDropdownValues == -1:
            if elementsDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "elementId" in queryString:
                    for elementId in map(int, queryString["elementId"]):
                        if len(list(filter(lambda elementTemplate: elementTemplate["value"] == elementId, elementsDropdownOptions))) > 0:
                            elementIds.append(elementId)
        else:
            if elementsDropdownOptions and elementsDropdownValues:
                for elementId in elementsDropdownValues:
                    if len(list(filter(lambda elementTemplate: elementTemplate["value"] == elementId, elementsDropdownOptions))) > 0:
                        elementIds.append(elementId)

        return elementIds

