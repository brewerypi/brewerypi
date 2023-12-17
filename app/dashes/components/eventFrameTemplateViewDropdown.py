from dash import dcc
from dash.dependencies import Input, Output
from urllib.parse import parse_qs, urlparse
from app.models import EventFrame, EventFrameTemplateView

def layout():
    return dcc.Dropdown(id = "eventFrameTemplateViewDropdown", placeholder = "Select View", multi = False)

def optionsCallback(dashApp, inputComponentId):
    @dashApp.callback(Output(component_id = "eventFrameTemplateViewDropdown", component_property = "options"),
        [Input(component_id = inputComponentId, component_property = "value")])
    def eventFrameTemplateViewDropdownOptions(eventFrameTemplateDropdownValue):
        if eventFrameTemplateDropdownValue is None:
            return []

        eventFrameTemplateViews = [{"label": eventFrameTemplateView.Name, "value": eventFrameTemplateView.EventFrameTemplateViewId}
            for eventFrameTemplateView in EventFrameTemplateView.query. \
                filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue, Selectable = True).order_by(EventFrameTemplateView.Order).all()]
        eventFrameTemplateViews.insert(0, {"label": "All", "value": -1})
        return eventFrameTemplateViews

def valueCallback(dashApp, inputComponentId):
    @dashApp.callback(Output(component_id = "eventFrameTemplateViewDropdown", component_property = "value"),
        [Input(component_id = inputComponentId, component_property = "value")])
    def eventFrameTemplateViewDropdownValue(eventFrameTemplateDropdownValue):
        defaultEventFrameTemplateView = EventFrameTemplateView.query.filter(EventFrameTemplateView.Default == True,
            EventFrameTemplateView.EventFrameTemplateId == eventFrameTemplateDropdownValue).one_or_none()
        if defaultEventFrameTemplateView is None:
            return -1
        else:
            return defaultEventFrameTemplateView.EventFrameTemplateViewId
