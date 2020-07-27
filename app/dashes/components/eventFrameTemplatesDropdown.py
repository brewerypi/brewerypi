import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import EventFrameTemplate

def layout():
    return dcc.Dropdown(id = "eventFrameTemplatesDropdown", placeholder = "Select Event Frame Template(s)", multi = True, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameTemplatesDropdown", component_property = "options"),
        [Input(component_id = "elementTemplatesDropdown", component_property = "value")])
    def eventFrameTemplatesDropdownOptions(elementTemplatesDropdownValues):
        return [{"label": eventFrameTemplate.Name, "value": eventFrameTemplate.EventFrameTemplateId} for eventFrameTemplate in EventFrameTemplate.query. \
            filter(EventFrameTemplate.ElementTemplateId.in_(elementTemplatesDropdownValues)).order_by(EventFrameTemplate.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameTemplatesDropdown", component_property = "value"),
        [Input(component_id = "eventFrameTemplatesDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "eventFrameTemplatesDropdown", component_property = "value")])
    def eventFrameTemplatesDropdownValues(eventFrameTemplatesDropdownOptions, urlHref, eventFrameTemplatesDropdownValues):
        eventFrameTemplateIds = []
        if eventFrameTemplatesDropdownValues == -1:
            if eventFrameTemplatesDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameTemplateId" in queryString:
                    for eventFrameTemplateId in map(int, queryString["eventFrameTemplateId"]):
                        if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == eventFrameTemplateId, eventFrameTemplatesDropdownOptions))) > 0:
                            eventFrameTemplateIds.append(eventFrameTemplateId)
        else:
            if eventFrameTemplatesDropdownOptions and eventFrameTemplatesDropdownValues:
                for eventFrameTemplateId in eventFrameTemplatesDropdownValues:
                    if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == eventFrameTemplateId, eventFrameTemplatesDropdownOptions))) > 0:
                        eventFrameTemplateIds.append(eventFrameTemplateId)

        return eventFrameTemplateIds
