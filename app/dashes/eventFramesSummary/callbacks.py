import dash
import dash_core_components as dcc
import pandas as pd
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import parse_qs, urlparse
from app import db
from app.dashes.components import collapseExpand, elementTemplatesDropdown, enterpriseDropdown, eventFrameTemplatesDropdown, eventFrameTemplateViewDropdown, \
    siteDropdown, timeRangePicker
from app.models import EventFrameTemplate
from .sql import eventFramesAttributeValues

def fromToTimestamp(fromTimestamp, toTimestamp, *args):
    updatedFromTimestamp = None
    urlHref = args[0]
    queryString = parse_qs(urlparse(urlHref).query)
    if "localTimezone" in queryString:
        localTimezone = pytz.timezone(queryString["localTimezone"][0])
    else:
        localTimezone = pytz.utc

    if "months" in queryString:
        months = int(queryString["months"][0])
        utcNow = pytz.utc.localize(datetime.utcnow())
        localNow = utcNow.astimezone(localTimezone)
        updatedFromTimestamp = (localNow - relativedelta(months = months))

    return fromTimestamp if updatedFromTimestamp is None else updatedFromTimestamp, toTimestamp

def registerCallbacks(dashApp):
    timeRangePicker.callback(dashApp, fromToTimestamp, [State(component_id = "url", component_property = "href")])
    collapseExpand.callback(dashApp)
    enterpriseDropdown.optionsCallback(dashApp)
    enterpriseDropdown.valueCallback(dashApp)
    siteDropdown.optionsCallback(dashApp)
    siteDropdown.valueCallback(dashApp)
    elementTemplatesDropdown.optionsCallback(dashApp)
    elementTemplatesDropdown.valuesCallback(dashApp)
    eventFrameTemplatesDropdown.optionsCallback(dashApp)
    eventFrameTemplatesDropdown.valuesCallback(dashApp)
    eventFrameTemplateViewDropdown.optionsCallback(dashApp, inputComponentId = "tabs")
    eventFrameTemplateViewDropdown.valueCallback(dashApp, inputComponentId = "tabs")
    
    @dashApp.callback(Output(component_id = "activeOnlyChecklist", component_property = "value"),
        [Input(component_id = "url", component_property = "href")])
    def activeOnlyChecklistValue(urlHref):
        if dash.callback_context.triggered[0]["prop_id"] == ".":
            raise PreventUpdate

        queryString = parse_qs(urlparse(urlHref).query)
        activeOnly = []
        if "activeOnly" in queryString:
            if queryString["activeOnly"][0] == "1":
                activeOnly = [1]

        return activeOnly

    @dashApp.callback([Output(component_id = "tabs", component_property = "children"),
        Output(component_id = "tabs", component_property = "value")],
        [Input(component_id = "eventFrameTemplatesDropdown", component_property = "value")])
    def tabsChildren(eventFrameTemplatesDropdownValues):
        children = []
        value = None
        for i, eventFrameTemplate in enumerate(EventFrameTemplate.query. \
            filter(EventFrameTemplate.EventFrameTemplateId.in_(eventFrameTemplatesDropdownValues)).order_by(EventFrameTemplate.Name)):
            if i == 0:
                value = eventFrameTemplate.EventFrameTemplateId

            if len(eventFrameTemplatesDropdownValues) > 1:
                label = f"{eventFrameTemplate.ElementTemplate.Name}_{eventFrameTemplate.Name}"
            else:
                label = eventFrameTemplate.Name

            children.append(dcc.Tab(label = label, value = eventFrameTemplate.EventFrameTemplateId))
        return children, value

    @dashApp.callback([Output(component_id = "loadingDiv", component_property = "style"),
        Output(component_id = "dashDiv", component_property = "style"),
        Output(component_id = "fromTimestampInput", component_property = "disabled"),
        Output(component_id = "toTimestampInput", component_property = "disabled"),
        Output(component_id = "timestampRangePickerButton", component_property = "disabled"),
        Output(component_id = "table", component_property = "columns"),
        Output(component_id = "table", component_property = "data")],
        [Input(component_id = "tabs", component_property = "value"),
        Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "activeOnlyChecklist", component_property = "value"),
        Input(component_id = "eventFrameTemplateViewDropdown", component_property = "value"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "fromTimestampInput", component_property = "disabled"),
        State(component_id = "toTimestampInput", component_property = "disabled"),
        State(component_id = "timestampRangePickerButton", component_property = "disabled")])
    def tableColumnsAndData(tabsValue, fromTimestampInputValue, toTimestampInputValue, activeOnlyChecklistValue, eventFrameTemplateViewDropdownValue,
        intervalNIntervals, refreshButtonNClicks, urlHref, fromTimestampInputDisabled, toTimestampInputDisabled, timestampRangePickerButtonDisabled):
        if  tabsValue is None:
            return {"display": "none"}, {"display": "block"}, fromTimestampInputDisabled, toTimestampInputDisabled, timestampRangePickerButtonDisabled, None, \
                None

        if activeOnlyChecklistValue:
            activeOnly = 1
            disabletimeRangePickerControls = True
        else:
            activeOnly = 0
            disabletimeRangePickerControls = False

        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
        toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

        df = pd.read_sql(eventFramesAttributeValues(tabsValue, eventFrameTemplateViewDropdownValue, fromTimestampUtc, toTimestampUtc, activeOnly),
            db.session.bind)
        df["Start"] = df["Start"].apply(lambda  timestamp: pytz.utc.localize(timestamp).astimezone(localTimezone).strftime("%Y-%m-%d %H:%M:%S"))
        df["End"] = df["End"].apply(lambda  timestamp: pytz.utc.localize(timestamp).astimezone(localTimezone).strftime("%Y-%m-%d %H:%M:%S")
            if pd.notnull(timestamp) else "")
        return {"display": "none"}, {"display": "block"}, disabletimeRangePickerControls, disabletimeRangePickerControls, disabletimeRangePickerControls, \
             [{"name": column, "id": column, "hideable": True} for column in df.columns], df.to_dict("records")
