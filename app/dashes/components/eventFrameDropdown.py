import pytz
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from sqlalchemy import or_
from urllib.parse import parse_qs, urlparse
from app.models import EventFrame

def layout():
    return dcc.Dropdown(id = "eventFrameDropdown", placeholder = "Select Event Frame", multi = False, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameDropdown", component_property = "options"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value"),
        Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value")],
        [State(component_id = "url", component_property = "href")])
    def eventFrameDropdownOptions(eventFrameTemplateDropdownValue, fromTimestampInputValue, toTimestampInputValue, urlHref):
        if fromTimestampInputValue == "" or toTimestampInputValue == "":
            raise PreventUpdate

        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
        toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

        return [{"label": eventFrame.Name, "value": eventFrame.EventFrameId} for eventFrame in EventFrame.query. \
            filter(EventFrame.EventFrameTemplateId == eventFrameTemplateDropdownValue, EventFrame.StartTimestamp >= fromTimestampUtc,
            or_(EventFrame.EndTimestamp <= toTimestampUtc, EventFrame.EndTimestamp == None)).order_by(EventFrame.StartTimestamp.desc()).all()]

def valueCallback(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameDropdown", component_property = "value"),
        [Input(component_id = "eventFrameDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "eventFrameDropdown", component_property = "value")])
    def eventFrameDropdownValue(eventFrameDropdownOptions, urlHref, eventFrameDropdownValue):
        if eventFrameDropdownValue == -1:
            # url href input fired.
            if eventFrameDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameId" in queryString:
                    eventFrameId = int(queryString["eventFrameId"][0])                
                    if len(list(filter(lambda eventFrame: eventFrame["value"] == eventFrameId, eventFrameDropdownOptions))) > 0:
                        return eventFrameId
        else:
            # eventFrameDropdown options input fired.
            if len(list(filter(lambda eventFrame: eventFrame["value"] == eventFrameDropdownValue, eventFrameDropdownOptions))) > 0:
                raise PreventUpdate

        return None
