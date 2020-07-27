import pandas as pd
import pytz
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
from urllib.parse import parse_qs, urlparse
from app import db
from app.dashes.components import collapseExpand, eventFrameGroupDropdown, eventFrameTemplateViewDropdown, refreshInterval
from app.models import EventFrameGroup
from app.models import EventFrame, EventFrameEventFrameGroup, EventFrameGroup, EventFrameTemplate
from .sql import eventFrameAttributeValues

def registerCallbacks(dashApp):
    refreshInterval.callback(dashApp)
    collapseExpand.callback(dashApp)
    eventFrameGroupDropdown.optionsCallback(dashApp)
    eventFrameGroupDropdown.valueCallback(dashApp)
    eventFrameTemplateViewDropdown.optionsCallback(dashApp, inputComponentId = "tabs")
    eventFrameTemplateViewDropdown.valueCallback(dashApp, inputComponentId = "tabs")

    @dashApp.callback([Output(component_id = "tabs", component_property = "children"),
        Output(component_id = "tabs", component_property = "value")],
        [Input(component_id = "eventFrameGroupDropdown", component_property = "value")])
    def tabsChildren(eventFrameGroupDropdownValue):
        children = []
        value = None
        eventFrameTemplates = EventFrameTemplate.query.join(EventFrame, EventFrameEventFrameGroup). \
            filter(EventFrameEventFrameGroup.EventFrameGroupId == eventFrameGroupDropdownValue).order_by(EventFrameTemplate.Name).all()
        for i, eventFrameTemplate in enumerate(eventFrameTemplates):
            if i == 0:
                value = eventFrameTemplate.EventFrameTemplateId

            label = f"{eventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation}_{eventFrameTemplate.ElementTemplate.Site.Abbreviation}_" + \
                f"{eventFrameTemplate.ElementTemplate.Name}_{eventFrameTemplate.Name}"
            children.append(dcc.Tab(label = label, value = eventFrameTemplate.EventFrameTemplateId))
        return children, value

    @dashApp.callback([Output(component_id = "loadingDiv", component_property = "style"),
        Output(component_id = "dashDiv", component_property = "style"),
        Output(component_id = "table", component_property = "columns"),
        Output(component_id = "table", component_property = "data")],
        [Input(component_id = "tabs", component_property = "value"),
        Input(component_id = "eventFrameGroupDropdown", component_property = "value"),
        Input(component_id = "eventFrameTemplateViewDropdown", component_property = "value"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")],
        [State(component_id = "url", component_property = "href")])
    def tableColumnsAndData(tabsValue, eventFrameGroupDropdownValue, eventFrameTemplateViewDropdownValue, intervalNIntervals, refreshButtonNClicks, urlHref):
        eventFrameGroup = EventFrameGroup.query.filter_by(EventFrameGroupId = eventFrameGroupDropdownValue).one_or_none()
        if eventFrameGroup is None or eventFrameGroup.EventFrameEventFrameGroups.count() == 0:
            return {"display": "none"}, {"display": "block"}, None, None           

        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        df = pd.read_sql(eventFrameAttributeValues(eventFrameGroup.EventFrameGroupId, tabsValue, eventFrameTemplateViewDropdownValue), db.session.bind)
        df["Start"] = df["Start"].apply(lambda  timestamp: pytz.utc.localize(timestamp).astimezone(localTimezone).strftime("%Y-%m-%d %H:%M:%S"))
        df["End"] = df["End"].apply(lambda timestamp: pytz.utc.localize(timestamp).astimezone(localTimezone).strftime("%Y-%m-%d %H:%M:%S")
            if timestamp is not pd.NaT and timestamp is not None else None)
        return {"display": "none"}, {"display": "block"}, [{"name": column, "id": column, "hideable": True} for column in df.columns], df.to_dict("records")
