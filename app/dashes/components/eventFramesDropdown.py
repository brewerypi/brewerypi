from dash import dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import EventFrame

def layout():
    return dcc.Dropdown(id = "eventFramesDropdown", placeholder = "Select Event Frame(s)", multi = True, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFramesDropdown", component_property = "options"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFramesDropdownOptions(eventFrameTemplateDropdownValue):
        return [{"label": eventFrame.Name, "value": eventFrame.EventFrameId} for eventFrame in
            EventFrame.query.filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue).order_by(EventFrame.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFramesDropdown", component_property = "value"),
        [Input(component_id = "eventFramesDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "eventFramesDropdown", component_property = "value")])
    def eventFramesDropdownValues(eventFramesDropdownOptions, urlHref, eventFramesDropdownValues):
        eventFrameIds = []
        if eventFramesDropdownValues == -1:
            if eventFramesDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameId" in queryString:
                    for eventFrameId in map(int, queryString["eventFrameId"]):
                        if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == eventFrameId, eventFramesDropdownOptions))) > 0:
                            eventFrameIds.append(eventFrameId)
        else:
            if eventFramesDropdownOptions and eventFramesDropdownValues:
                for eventFrameId in eventFramesDropdownValues:
                    if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == eventFrameId, eventFramesDropdownOptions))) > 0:
                        eventFrameIds.append(eventFrameId)

        return eventFrameIds
