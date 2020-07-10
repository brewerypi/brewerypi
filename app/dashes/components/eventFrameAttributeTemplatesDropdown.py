import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import EventFrameAttributeTemplate

def layout():
    return dcc.Dropdown(id = "eventFrameAttributeTemplatesDropdown", placeholder = "Select Event Frame Attribute Template(s)", multi = True)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "options"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameAttributeTemplatesDropdownOptions(eventFrameTemplateDropdownValue):
        eventFrameAttributeTemplates = [{"label": eventFrameAttributeTemplate.Name, "value": eventFrameAttributeTemplate.EventFrameAttributeTemplateId}
            for eventFrameAttributeTemplate in EventFrameAttributeTemplate.query.filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue). \
                order_by(EventFrameAttributeTemplate.Name).all()]
        eventFrameAttributeTemplates.insert(0, {"label": "All", "value": -1})
        return eventFrameAttributeTemplates

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "value"),
        [Input(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "value")])
    def eventFramesDropdownValues(eventFrameAttributeTemplatesDropdownOptions, urlHref, eventFramesDropdownValues):
        eventFrameAttributeTemplateIds = []
        if eventFramesDropdownValues == -1:
            if eventFrameAttributeTemplatesDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameAttributeTemplateId" in queryString:
                    for eventFrameAttributeTemplateId in map(int, queryString["eventFrameAttributeTemplateId"]):
                        if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == eventFrameAttributeTemplateId,
                            eventFrameAttributeTemplatesDropdownOptions))) > 0:
                            eventFrameAttributeTemplateIds.append(eventFrameAttributeTemplateId)
        else:
            if eventFrameAttributeTemplatesDropdownOptions and eventFramesDropdownValues:
                for eventFrameAttributeTemplateId in eventFramesDropdownValues:
                    if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == eventFrameAttributeTemplateId,
                        eventFrameAttributeTemplatesDropdownOptions))) > 0:
                        eventFrameAttributeTemplateIds.append(eventFrameAttributeTemplateId)

        return eventFrameAttributeTemplateIds

