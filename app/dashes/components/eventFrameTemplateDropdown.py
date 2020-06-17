import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
from urllib.parse import parse_qs, urlparse
from app.models import EventFrameTemplate

def layout():
    return dcc.Dropdown(id = "eventFrameTemplateDropdown", placeholder = "Select Event Frame Template", multi = False)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameTemplateDropdown", component_property = "options"),
        [Input(component_id = "elementTemplateDropdown", component_property = "value")])
    def eventFrameTemplateDropdownOptions(elementTemplateDropdownValue):
        return [{"label": eventFrameTemplate.Name, "value": eventFrameTemplate.EventFrameTemplateId} for eventFrameTemplate in EventFrameTemplate.query. \
            filter(EventFrameTemplate.ElementTemplateId == elementTemplateDropdownValue).order_by(EventFrameTemplate.Name).all()]

def valueCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameTemplateDropdown", component_property = "value"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
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
