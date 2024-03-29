import dash
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dateutil.relativedelta import relativedelta
from urllib.parse import parse_qs, urlparse
from app.models import EventFrame, EventFrameAttribute, EventFrameNote, EventFrameTemplateView, LookupValue, Note, TagValue
from app.dashes.components import collapseExpand, elementTemplateDropdown, enterpriseDropdown, eventFrameDropdown, eventFrameTemplateDropdown, \
    eventFrameTemplateViewDropdown, siteDropdown, timeRangePicker

def fromToTimestamp(fromTimestamp, toTimestamp, *args):
    if dash.callback_context.triggered[0]["prop_id"] == ".":
        raise PreventUpdate

    updatedFromTimestamp = None
    updatedToTimestamp = None
    if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
        # url href input fired.
        urlHref = args[0]
        queryString = parse_qs(urlparse(urlHref).query)
        if "eventFrameId" in queryString:
            eventFrameId = int(queryString["eventFrameId"][0])
            eventFrame = EventFrame.query.get(eventFrameId)
            if eventFrame is not None:
                queryString = parse_qs(urlparse(urlHref).query)
                if "localTimezone" in queryString:
                    localTimezone = pytz.timezone(queryString["localTimezone"][0])
                else:
                    localTimezone = pytz.utc

                updatedFromTimestamp = eventFrame.StartTimestamp.astimezone(localTimezone)
                if eventFrame.EndTimestamp is not None:
                    # A closed event frame exists so use the end timestamp.
                    updatedToTimestamp = (eventFrame.EndTimestamp + relativedelta(minutes = 1)).astimezone(localTimezone)
    elif len(list(filter(lambda property: property["prop_id"] == "interval.n_intervals", dash.callback_context.triggered))) > 0:
        # interval n_intervals input fired.
        eventFrameDropdownValue = args[1]
        if eventFrameDropdownValue is not None:
            eventFrame = EventFrame.query.get(eventFrameDropdownValue)
            if eventFrame is not None:
                if eventFrame.EndTimestamp is not None:
                    raise PreventUpdate

    return fromTimestamp if updatedFromTimestamp is None else updatedFromTimestamp, toTimestamp if updatedToTimestamp is None else updatedToTimestamp

def registerCallbacks(dashApp):
    timeRangePicker.callback(dashApp, fromToTimestamp, [State(component_id = "url", component_property = "href"),
        State(component_id = "eventFrameDropdown", component_property = "value")])
    collapseExpand.callback(dashApp)
    enterpriseDropdown.optionsCallback(dashApp)
    enterpriseDropdown.valueCallback(dashApp)
    siteDropdown.optionsCallback(dashApp)
    siteDropdown.valueCallback(dashApp)
    elementTemplateDropdown.optionsCallback(dashApp)
    elementTemplateDropdown.valueCallback(dashApp)
    eventFrameTemplateDropdown.optionsCallback(dashApp)
    eventFrameTemplateDropdown.valueCallback(dashApp)
    eventFrameDropdown.optionsCallback(dashApp)
    eventFrameDropdown.valueCallback(dashApp)
    eventFrameTemplateViewDropdown.optionsCallback(dashApp, "eventFrameTemplateDropdown")
    eventFrameTemplateViewDropdown.valueCallback(dashApp, "eventFrameTemplateDropdown")

    @dashApp.callback([Output(component_id = "loadingDiv", component_property = "style"),
        Output(component_id = "dashDiv", component_property = "style"),
        Output(component_id = "fromToTimestampsDiv", component_property = "style"),
        Output(component_id = "quickTimeRangePickerDiv", component_property = "style"),
        Output(component_id = "graph", component_property = "figure"),
        Output(component_id = "table", component_property = "data")],
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "eventFrameDropdown", component_property = "value"),
        Input(component_id = "eventFrameTemplateViewDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")],
        [State(component_id = "fromToTimestampsDiv", component_property = "style"),
        State(component_id = "quickTimeRangePickerDiv", component_property = "style")])
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, eventFrameDropdownValue, eventFrameTemplateViewDropdownValue, urlHref, intervalNIntervals,
        refreshButtonNClicks, fromToTimestampsDivStyle, quickTimeRangePickerDivStyle):
        if eventFrameDropdownValue is None:
            return {"display": "none"}, {"display": "block"}, fromToTimestampsDivStyle, quickTimeRangePickerDivStyle, {"data": []}, []

        if fromTimestampInputValue == "" or toTimestampInputValue == "":
            raise PreventUpdate

        eventFrame = EventFrame.query.get(eventFrameDropdownValue)
        data = []
        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        if eventFrameTemplateViewDropdownValue == -1:
            eventFrameAttributeTemplateIds = [eventFrameAttributeTemplate.EventFrameAttributeTemplateId
                for eventFrameAttributeTemplate in eventFrame.EventFrameTemplate.EventFrameAttributeTemplates]
        else:
            eventFrameTemplateView = EventFrameTemplateView.query.get(eventFrameTemplateViewDropdownValue)
            eventFrameAttributeTemplateIds = [eventFrameAttributeTemplateEventFrameTemplateView.EventFrameAttributeTemplateId
                for eventFrameAttributeTemplateEventFrameTemplateView in eventFrameTemplateView.EventFrameAttributeTemplateEventFrameTemplateViews]

        eventFrameAttributes = EventFrameAttribute.query.filter(EventFrameAttribute.ElementId == eventFrame.ElementId,
            EventFrameAttribute.EventFrameAttributeTemplateId.in_(eventFrameAttributeTemplateIds))
        eventFrameAttributeValues = {}
        for eventFrameAttribute in eventFrameAttributes:
            if eventFrame.EndTimestamp is None:
                eventFrameAttributeValues[eventFrameAttribute.EventFrameAttributeTemplate.Name] = TagValue.query. \
                    filter(TagValue.TagId == eventFrameAttribute.TagId, TagValue.Timestamp >= eventFrame.StartTimestamp)
            else:
                eventFrameAttributeValues[eventFrameAttribute.EventFrameAttributeTemplate.Name] = TagValue.query. \
                    filter(TagValue.TagId == eventFrameAttribute.TagId, TagValue.Timestamp >= eventFrame.StartTimestamp,
                        TagValue.Timestamp <= eventFrame.EndTimestamp)

        for eventFrameAttributeTemplateName, tagValues in eventFrameAttributeValues.items():
            seriesName = eventFrameAttributeTemplateName
            for tagValue in tagValues:
                # Search for tag dict in list of dicts.
                listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == seriesName, data))
                if len(listOfDictionaries) == 0:
                    # Tag dict doesn't exist so append it to the list of dicts.
                    if tagValue.Tag.LookupId is None:
                        data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                            y = [tagValue.Value],
                            text = [tagValue.Tag.UnitOfMeasurement.Abbreviation],
                            name = seriesName,
                            mode = "lines+markers"))
                    else:
                        data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                            y = [tagValue.Value],
                            text = [LookupValue.query.filter_by(LookupId = tagValue.Tag.LookupId, Value = tagValue.Value).one().Name],
                            name = seriesName,
                            mode = "lines+markers"))
                else:
                    # Tag dict already exists so append to x, y and text.
                    tagDictionary = listOfDictionaries[0]
                    tagDictionary["x"].append(pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone))
                    tagDictionary["y"].append(tagValue.Value)
                    if tagValue.Tag.LookupId is None:
                        tagDictionary["text"].append(tagValue.Tag.UnitOfMeasurement.Abbreviation)
                    else:
                        tagDictionary["text"].append(LookupValue.query.filter_by(LookupId = tagValue.Tag.LookupId, Value = tagValue.Value).one().Name)

                if tagValue.TagValueNotes.count() > 0:
                    tagValueNotes = ""
                    for n, tagValueNote in enumerate(tagValue.TagValueNotes, start = 1):
                        note = "{}: {}".format(pytz.utc.localize(tagValueNote.Note.Timestamp).astimezone(localTimezone), tagValueNote.Note.Note)
                        if n != 1:
                            note = "<br>" + note
                        
                        tagValueNotes = tagValueNotes + note

                    # Search for tag notes dict in list of dicts.
                    listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == "{} Notes".format(seriesName), data))
                    if len(listOfDictionaries) == 0:
                        # Tag notes dict doesn't exist so append it to the list of dicts.
                        data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                            y = [tagValue.Value],
                            text = [tagValueNotes],
                            name = "{} Notes".format(seriesName),
                            mode = "markers"))
                    else:
                        # Tag notes dict already exists so append to x, y and text.
                        tagNotesDictionary = listOfDictionaries[0]
                        tagNotesDictionary["x"].append(pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone))
                        tagNotesDictionary["y"].append(tagValue.Value)
                        tagNotesDictionary["text"].append(tagValueNotes)

            eventFrameStartTimestamp = pytz.utc.localize(eventFrame.StartTimestamp).astimezone(localTimezone)
            shapes = [dict(type = "line", yref = "paper", y0 = 0, y1 = 1, x0 = eventFrameStartTimestamp, x1 = eventFrameStartTimestamp, line =
                dict(width = 1, dash = "dot"))]
            if eventFrame.EndTimestamp is not None:
                eventFrameEndTimestamp = pytz.utc.localize(eventFrame.EndTimestamp).astimezone(localTimezone)
                shapes.append(dict(type = "line", yref = "paper", y0 = 0, y1 = 1, x0 = eventFrameEndTimestamp, x1 = eventFrameEndTimestamp,
                    line = dict(width = 1, dash = "dot")))

            eventFrameNotes = []
            for eventFrameNote in Note.query.join(EventFrameNote).filter(EventFrameNote.EventFrameId == eventFrame.EventFrameId).order_by(Note.Timestamp):
                eventFrameNotes.append({"Timestamp": pytz.utc.localize(eventFrameNote.Timestamp).astimezone(localTimezone).strftime("%Y-%m-%d %H:%M:%S"),
                    "Note": eventFrameNote.Note})

        return {"display": "none"}, {"display": "block"}, {"display": "none"} if "eventFrameId" in queryString else fromToTimestampsDivStyle, \
            {"display": "none"} if "eventFrameId" in queryString else quickTimeRangePickerDivStyle, \
                {"data": data, "layout": {"shapes": shapes, "uirevision": "no reset"}}, eventFrameNotes
