import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import EventFrameAttributeTemplate

def layout():
    return html.Div(children =
    [
        html.Button(id = "eventFrameAttributeTemplatesDropdownSelectAllButton", className = "btn btn-default btn-sm", type = "button", n_clicks = 0, children = ["Select All"]),
        html.Button(id = "eventFrameAttributeTemplatesDropdownClearAllButton", className = "btn btn-default btn-sm", type = "button", n_clicks = 0, children = ["Clear All"]),
        dcc.Dropdown(id = "eventFrameAttributeTemplatesDropdown", placeholder = "Select Event Frame Attribute Template(s)", multi = True)
    ])

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "options"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameAttributeTemplatesDropdownOptions(eventFrameTemplateDropdownValue):
        eventFrameAttributeTemplates = [{"label": eventFrameAttributeTemplate.Name, "value": eventFrameAttributeTemplate.EventFrameAttributeTemplateId}
            for eventFrameAttributeTemplate in EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue). \
                order_by(EventFrameAttributeTemplate.Name).all()]
        return eventFrameAttributeTemplates

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "value"),
        [Input(component_id = "eventFrameAttributeTemplatesDropdownSelectAllButton", component_property = "n_clicks"),
        Input(component_id = "eventFrameAttributeTemplatesDropdownClearAllButton", component_property = "n_clicks")],
        [State(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "options")])
    def eventFramesDropdownValues(eventFrameAttributeTemplatesDropdownSelectAllButtonNClicks, eventFrameAttributeTemplatesDropdownClearAllButtonNClicks,
        eventFrameAttributeTemplatesDropdownOptions):
        eventFrameAttributeTemplateIds = []
        componentId = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
        if componentId == "eventFrameAttributeTemplatesDropdownSelectAllButton":
            eventFrameAttributeTemplateIds = [eventFrameAttributeTemplatesDropdownOption["value"]
                for eventFrameAttributeTemplatesDropdownOption in eventFrameAttributeTemplatesDropdownOptions]

        return eventFrameAttributeTemplateIds
