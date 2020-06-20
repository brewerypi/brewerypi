import dash_core_components as dcc
from dash.dependencies import Input, Output
from urllib.parse import parse_qs, urlparse
from app.models import EventFrameTemplateView

def layout():
    return dcc.Dropdown(id = "eventFrameTemplateViewDropdown", placeholder = "Select View", multi = False)

def registerOptionsValueCallback(dashApp):
    @dashApp.callback([Output(component_id = "eventFrameTemplateViewDropdown", component_property = "options"),
        Output(component_id = "eventFrameTemplateViewDropdown", component_property = "value")],
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameTemplateViewDropdownOptionsValue(eventFrameTemplateDropdownValue):
        if eventFrameTemplateDropdownValue is None:
            return [[], None]

        eventFrameTemplateViews = [{"label": eventFrameTemplateView.Name, "value": eventFrameTemplateView.EventFrameTemplateViewId}
            for eventFrameTemplateView in EventFrameTemplateView.query.filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue). \
                order_by(EventFrameTemplateView.Name).all()]
        eventFrameTemplateViews.insert(0, {"label": "All", "value": -1})
        return [eventFrameTemplateViews, -1]
