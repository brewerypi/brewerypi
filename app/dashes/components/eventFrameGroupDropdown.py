import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import EventFrameGroup

def layout():
    return dcc.Dropdown(id = "eventFrameGroupDropdown", placeholder = "Select Event Frame Group", multi = False, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameGroupDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def eventFrameGroupDropdownOptions(urlHref):
        return [{"label": eventFrameGroup.Name, "value": eventFrameGroup.EventFrameGroupId} for eventFrameGroup in EventFrameGroup.query. \
            order_by(EventFrameGroup.Name).all()]

def valueCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameGroupDropdown", component_property = "value"),
        [Input(component_id = "eventFrameGroupDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "eventFrameGroupDropdown", component_property = "value")])
    def eventFrameGroupDropdownValue(eventFrameGroupDropdownOptions, urlHref, eventFrameGroupDropdownValue):
        eventFrameGroupId = None
        if eventFrameGroupDropdownValue == -1:
            if eventFrameGroupDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameGroupId" in queryString:
                    id = int(queryString["eventFrameGroupId"][0])                
                    if len(list(filter(lambda eventFrameGroup: eventFrameGroup["value"] == id, eventFrameGroupDropdownOptions))) > 0:
                        eventFrameGroupId = id

        return eventFrameGroupId
