import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from sqlalchemy import and_, case, or_
from urllib.parse import parse_qs, urlparse
from app.dashes.components import collapseExpand, elementTemplateDropdown, enterpriseDropdown, eventFrameAttributeTemplateDropdown, \
    eventFrameTemplateDropdown, siteDropdown, timeRangePicker
from app.models import Element, EventFrame, EventFrameAttribute, EventFrameAttributeTemplate, EventFrameTemplate, Lookup, LookupValue, Tag, TagValue

def registerCallbacks(dashApp):
    timeRangePicker.callback(dashApp)
    collapseExpand.callback(dashApp)
    enterpriseDropdown.optionsCallback(dashApp)
    enterpriseDropdown.valueCallback(dashApp)
    siteDropdown.optionsCallback(dashApp)
    siteDropdown.valueCallback(dashApp)
    elementTemplateDropdown.optionsCallback(dashApp)
    elementTemplateDropdown.valueCallback(dashApp)
    eventFrameTemplateDropdown.optionsCallback(dashApp)
    eventFrameTemplateDropdown.valueCallback(dashApp)

    @dashApp.callback(Output(component_id = "subgroupLookupDropdown", component_property = "options"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = 'value')])
    def subgroupLookupDropdownOptions(eventFrameTemplateDropdownValue):
        subgroupLookups = [{"label": eventFrameAttributeTemplate.Name, "value": eventFrameAttributeTemplate.Lookup.LookupId}
        for eventFrameAttributeTemplate in EventFrameAttributeTemplate.query.join(Lookup). \
            filter(EventFrameAttributeTemplate.EventFrameTemplateId == eventFrameTemplateDropdownValue, Lookup.LookupId is not None). \
            order_by(EventFrameAttributeTemplate.Name).all()]

        return subgroupLookups

    @dashApp.callback(Output(component_id = "subgroupLookupValueDropdown", component_property = "options"),
        [Input(component_id = "subgroupLookupDropdown", component_property = 'value')])
    def subgroupLookupValueDropdownOptions(subgroupLookupDropdownValue):
        subgroupLookupValues = [{"label": lookupValue.Name, "value": lookupValue.Value}
        for lookupValue in LookupValue.query.filter(LookupValue.LookupId == subgroupLookupDropdownValue).order_by(LookupValue.Name).all()]

        return subgroupLookupValues

    eventFrameAttributeTemplateDropdown.optionsCallback(dashApp)

    @dashApp.callback([Output(component_id = "loadingDiv", component_property = "style"),
        Output(component_id = "dashDiv", component_property = "style"),
        Output(component_id = "individualGraph", component_property = "figure"),
        Output(component_id = "movingRangeGraph", component_property = "figure")],
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "eventFrameTemplateDropdown", component_property = "value"),
        Input(component_id = "subgroupLookupDropdown", component_property = "value"),
        Input(component_id = "subgroupLookupValueDropdown", component_property = "value"),
        Input(component_id = "eventFrameAttributeTemplateDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def graphFigures(fromTimestampInputValue, toTimestampInputValue, eventFrameTemplateDropdownValue, subgroupLookupDropdownValue,
            subgroupLookupValueDropdownValue, eventFrameAttributeTemplateDropdownValue, urlHref, intervalNIntervals, refreshButtonNClicks):
        if eventFrameTemplateDropdownValue == -1 or eventFrameTemplateDropdownValue is None or \
            subgroupLookupDropdownValue == -1 or subgroupLookupDropdownValue is None or \
            subgroupLookupValueDropdownValue == -1 or subgroupLookupValueDropdownValue is None or \
            eventFrameAttributeTemplateDropdownValue == -1 or eventFrameAttributeTemplateDropdownValue is None:
            return {"display": "none"}, {"display": "block"}, {"data": []}, {"data": []}

        if fromTimestampInputValue is None or toTimestampInputValue is None:
            raise PreventUpdate
        else:
            individualData = []
            movingRangeData = []
            if fromTimestampInputValue != "" and toTimestampInputValue != "":
                queryString = parse_qs(urlparse(urlHref).query)
                if "localTimezone" in queryString:
                    localTimezone = pytz.timezone(queryString["localTimezone"][0])
                else:
                    localTimezone = pytz.utc

                fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
                toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

                subgroupEventFrames = EventFrame.query. \
                    join(EventFrameTemplate). \
                    join(EventFrameAttributeTemplate). \
                    join(EventFrameAttribute). \
                    join(Element, and_(EventFrame.ElementId == Element.ElementId, EventFrameAttribute.ElementId == Element.ElementId)). \
                    join(Tag). \
                    join(TagValue). \
                    filter \
                    (
                        EventFrameTemplate.EventFrameTemplateId == eventFrameTemplateDropdownValue,
                        Tag.LookupId == subgroupLookupDropdownValue,
                        TagValue.Value == subgroupLookupValueDropdownValue,
                        EventFrame.StartTimestamp >= fromTimestampUtc,
                        or_
                        (
                            EventFrame.EndTimestamp <= toTimestampUtc,
                            EventFrame.EndTimestamp == None
                        ),
                        TagValue.Timestamp >= EventFrame.StartTimestamp,
                        case
                        (
                            (EventFrame.EndTimestamp != None, TagValue.Timestamp <= EventFrame.EndTimestamp),
                            else_ = TagValue.Timestamp >= EventFrame.StartTimestamp
                        )
                    )
                
                subgroupEventFramesIds = [subgroupEventFrameId.EventFrameId for subgroupEventFrameId in subgroupEventFrames]
                tagValues = TagValue.query. \
                    join(Tag). \
                    join(EventFrameAttribute). \
                    join(Element). \
                    join(EventFrameAttributeTemplate). \
                    join(EventFrameTemplate). \
                    join(EventFrame,
                         and_(Element.ElementId == EventFrame.ElementId, EventFrameTemplate.EventFrameTemplateId == EventFrame.EventFrameTemplateId)). \
                    filter \
                    (
                        EventFrame.EventFrameId.in_(subgroupEventFramesIds),
                        EventFrameAttributeTemplate.EventFrameAttributeTemplateId == eventFrameAttributeTemplateDropdownValue,
                        EventFrame.StartTimestamp >= fromTimestampUtc,
                        or_
                        (
                            EventFrame.EndTimestamp <= toTimestampUtc,
                            EventFrame.EndTimestamp == None
                        ),
                        TagValue.Timestamp >= EventFrame.StartTimestamp,
                        case
                        (
                            (EventFrame.EndTimestamp != None, TagValue.Timestamp <= EventFrame.EndTimestamp),
                            else_ = TagValue.Timestamp >= EventFrame.StartTimestamp
                        )
                    ). \
                    order_by(TagValue.Timestamp). \
                    with_entities(EventFrame.Name.label("EventFrameName"), TagValue.Timestamp, TagValue.Value).all()

                individualX = []
                movingRangeX = []
                individualY = []
                movingRangeY = []
                individualText = []
                n = 0
                processSum = 0
                previousValue = None
                movingRangeSum = 0
                for tagValue in tagValues:
                    n = n + 1
                    individualX.append(n)
                    processSum = processSum + tagValue.Value
                    individualY.append(tagValue.Value)
                    text = "Event Frame: " + tagValue.EventFrameName + " timestamp: " + \
                        pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone).strftime("%Y-%m-%d %H:%M:%S")

                    individualText.append(text)
                    if previousValue is not None:
                        movingRangeX.append(n)
                        absoluteDifference = abs(tagValue.Value - previousValue)
                        movingRangeSum = movingRangeSum + absoluteDifference
                        movingRangeY.append(absoluteDifference)
                    previousValue = tagValue.Value

                eventFrameAttributeTemplate = EventFrameAttributeTemplate.query. \
                    filter(EventFrameAttributeTemplate.EventFrameAttributeTemplateId == eventFrameAttributeTemplateDropdownValue).one_or_404()
                individualData.append(dict(x = individualX, y = individualY, text = individualText, name = eventFrameAttributeTemplate.Name,
                    mode = "lines+markers", line = dict(shape = "linear", color = "black")))

                if n > 0:
                    processAverage = processSum / n
                    individualData.append(dict(x = [1, n], y = [processAverage, processAverage], name = "average", mode = "lines+markers",
                        line = dict(shape = "linear", color = "green")))

                if n > 1:
                    movingRangeData.append(dict(x = movingRangeX, y = movingRangeY, name = eventFrameAttributeTemplate.Name, mode = "lines+markers",
                        line = dict(shape = "linear", color = "black")))
                    movingRange = movingRangeSum / (n - 1)
                    individualUcl = processAverage + (2.66 * movingRange)
                    individualLcl = processAverage - (2.66 * movingRange)
                    individualData.append(dict(x = [1, n], y = [individualUcl, individualUcl], name = "UCL", mode = "lines+markers",
                        line = dict(shape = "linear", color = "yellow")))
                    individualData.append(dict(x = [1, n], y = [individualLcl, individualLcl], name = "LCL", mode = "lines+markers",
                        line = dict(shape = "linear", color = "yellow")))
                    movingRangeUcl = 3.27 * movingRange
                    movingRangeLcl = 0 * movingRange
                    movingRangeData.append(dict(x = [1, n], y = [movingRange, movingRange], name = "moving range", mode = "lines+markers",
                        line = dict(shape = "linear", color = "green")))
                    movingRangeData.append(dict(x = [1, n], y = [movingRangeUcl, movingRangeUcl], name = "UCL", mode = "lines+markers",
                        line = dict(shape = "linear", color = "yellow")))
                    movingRangeData.append(dict(x = [1, n], y = [movingRangeLcl, movingRangeLcl], name = "LCL", mode = "lines+markers",
                        line = dict(shape = "linear", color = "yellow")))

            return {"display": "none"}, {"display": "block"}, {"data": individualData, "layout": {"uirevision": "no reset"}}, \
                {"data": movingRangeData, "layout": {"uirevision": "no reset"}}
