import pandas as pd
import pytz
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
from urllib.parse import parse_qs, urlparse
from app import db
from app.dashes.components import collapseExpand, elementTemplatesDropdown, enterpriseDropdown, eventFrameTemplatesDropdown, eventFrameTemplateViewDropdown, \
    refreshInterval, siteDropdown
from app.models import EventFrameTemplate
from .sql import activeEventFrameAttributeValues

def registerCallbacks(dashApp):
    refreshInterval.callback(dashApp)
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
    
    @dashApp.callback([Output(component_id = "tabs", component_property = "children"),
        Output(component_id = "tabs", component_property = "value")],
        [Input(component_id = "eventFrameTemplatesDropdown", component_property = "value")])
    def tabsChildren(eventFrameTemplatesDropdownValues):
        children = []
        value = None
        for i, eventFrameTemplate in enumerate(EventFrameTemplate.query.filter(EventFrameTemplate.EventFrameTemplateId.in_(eventFrameTemplatesDropdownValues)) \
            .order_by(EventFrameTemplate.Name)):
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
        Output(component_id = "table", component_property = "columns"),
        Output(component_id = "table", component_property = "data")],
        [Input(component_id = "tabs", component_property = "value"),
        Input(component_id = "eventFrameTemplateViewDropdown", component_property = "value"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")],
        [State(component_id = "url", component_property = "href")])
    def tableColumnsAndData(tabsValue, eventFrameTemplateViewDropdownValue, intervalNIntervals, refreshButtonNClicks, urlHref):
        if  tabsValue is None:
            return {"display": "none"}, {"display": "block"}, None, None

        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        df = pd.read_sql(activeEventFrameAttributeValues(tabsValue, eventFrameTemplateViewDropdownValue), db.session.bind)
        df["Start"] = df["Start"].apply(lambda  timestamp: pytz.utc.localize(timestamp).astimezone(localTimezone).strftime("%Y-%m-%d %H:%M:%S"))
        return {"display": "none"}, {"display": "block"}, [{"name": column, "id": column, "hideable": True} for column in df.columns], df.to_dict("records")
