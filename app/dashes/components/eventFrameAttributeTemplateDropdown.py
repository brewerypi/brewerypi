from dash import dcc
from dash import html
from dash.dependencies import Input, Output
from app.models import EventFrameAttributeTemplate

def layout():
    return html.Div(children =
    [
        dcc.Dropdown(id = "eventFrameAttributeTemplateDropdown", placeholder = "Select Event Frame Attribute Template", multi = False, value = -1)
    ])

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameAttributeTemplateDropdown", component_property = "options"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameAttributeTemplateDropdownOptions(eventFrameTemplateDropdownValue):
        eventFrameAttributeTemplates = [{"label": eventFrameAttributeTemplate.Name, "value": eventFrameAttributeTemplate.EventFrameAttributeTemplateId}
            for eventFrameAttributeTemplate in EventFrameAttributeTemplate.query. \
                filter(EventFrameAttributeTemplate.EventFrameTemplateId == eventFrameTemplateDropdownValue). \
                order_by(EventFrameAttributeTemplate.Name).all()]

        return eventFrameAttributeTemplates
