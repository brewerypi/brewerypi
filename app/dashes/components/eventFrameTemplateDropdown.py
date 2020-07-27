import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import EventFrameTemplate

def layout():
    return dcc.Dropdown(id = "eventFrameTemplateDropdown", placeholder = "Select Event Frame Template", multi = False, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameTemplateDropdown", component_property = "options"),
        [Input(component_id = "elementTemplateDropdown", component_property = "value")])
    def eventFrameTemplateDropdownOptions(elementTemplateDropdownValue):
        return [{"label": eventFrameTemplate.Name, "value": eventFrameTemplate.EventFrameTemplateId} for eventFrameTemplate in EventFrameTemplate.query. \
            filter(EventFrameTemplate.ElementTemplateId == elementTemplateDropdownValue).order_by(EventFrameTemplate.Name).all()]

def valueCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameTemplateDropdown", component_property = "value"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameTemplateDropdownValue(eventFrameTemplateDropdownOptions, urlHref, eventFrameTemplateDropdownValue):
        eventFrameTemplateId = None
        if eventFrameTemplateDropdownValue == -1:
            if eventFrameTemplateDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameTemplateId" in queryString:
                    id = int(queryString["eventFrameTemplateId"][0])                
                    if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == id, eventFrameTemplateDropdownOptions))) > 0:
                        eventFrameTemplateId = id

        return eventFrameTemplateId
