import dash
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_
from urllib.parse import parse_qs, urlparse
from app.models import ElementTemplate, Enterprise, EventFrame, EventFrameNote, EventFrameTemplate, EventFrameTemplateView, LookupValue, Note, Site
from app.dashes import timestampRangeComponent

def registerCallbacks(dashApp):
    @dashApp.callback([Output(component_id = "fromTimestampInput", component_property = "value"),
        Output(component_id = "toTimestampInput", component_property = "value")],
        [Input(component_id = "url", component_property = "href"),
        Input(component_id = "lastFiveMinutesLi", component_property = "n_clicks"),
        Input(component_id = "lastFifthteenMinutesLi", component_property = "n_clicks"),
        Input(component_id = "lastThirtyMinutesLi", component_property = "n_clicks"),
        Input(component_id = "lastOneHourLi", component_property = "n_clicks"),
        Input(component_id = "lastThreeHoursLi", component_property = "n_clicks"),
        Input(component_id = "lastSixHoursLi", component_property = "n_clicks"),
        Input(component_id = "lastTwelveHoursLi", component_property = "n_clicks"),
        Input(component_id = "lastTwentyFourHoursLi", component_property = "n_clicks"),
        Input(component_id = "lastTwoDaysLi", component_property = "n_clicks"),
        Input(component_id = "lastSevenDaysLi", component_property = "n_clicks"),
        Input(component_id = "lastThirtyDaysLi", component_property = "n_clicks"),
        Input(component_id = "lastNinetyDaysLi", component_property = "n_clicks"),
        Input(component_id = "lastSixMonthsLi", component_property = "n_clicks"),
        Input(component_id = "lastOneYearLi", component_property = "n_clicks"),
        Input(component_id = "lastTwoYearsLi", component_property = "n_clicks"),
        Input(component_id = "lastFiveYearsLi", component_property = "n_clicks"),
        Input(component_id = "yesterdayLi", component_property = "n_clicks"),
        Input(component_id = "dayBeforeYesterdayLi", component_property = "n_clicks"),
        Input(component_id = "thisDayLastWeekLi", component_property = "n_clicks"),
        Input(component_id = "previousWeekLi", component_property = "n_clicks"),
        Input(component_id = "previousMonthLi", component_property = "n_clicks"),
        Input(component_id = "previousYearLi", component_property = "n_clicks"),
        Input(component_id = "todayLi", component_property = "n_clicks"),
        Input(component_id = "todaySoFarLi", component_property = "n_clicks"),
        Input(component_id = "thisWeekLi", component_property = "n_clicks"),
        Input(component_id = "thisWeekSoFarLi", component_property = "n_clicks"),
        Input(component_id = "thisMonthLi", component_property = "n_clicks"),
        Input(component_id = "thisMonthSoFarLi", component_property = "n_clicks"),
        Input(component_id = "thisYearLi", component_property = "n_clicks"),
        Input(component_id = "thisYearSoFarLi", component_property = "n_clicks"),
        Input(component_id = "interval", component_property = "n_intervals")],
        [State(component_id = "fromTimestampInput", component_property = "value"),
        State(component_id = "eventFrameDropdown", component_property = "value")])
    def fromTimestampInputValueToTimestampInputValue(*args, **kwargs):
        timestamps = timestampRangeComponent.rangePickerCallback(*args[:-1], **kwargs)
        fromTimestamp = timestamps[0]
        toTimestamp = timestamps[1]
        urlHref = args[0]
        queryString = parse_qs(urlparse(urlHref).query)
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            # url href input fired.
            if "eventFrameId" in queryString:
                eventFrameId = int(queryString["eventFrameId"][0])
                eventFrame = EventFrame.query.get(eventFrameId)
                if eventFrame is not None:
                    fromTimestamp = eventFrame.StartTimestamp.strftime("%Y-%m-%dT%H:%M:%S")
                    if eventFrame.EndTimestamp is not None:
                        # A closed event frame exists so use the end timestamp.
                        toTimestamp = (eventFrame.EndTimestamp + relativedelta(minutes = 1)).strftime("%Y-%m-%dT%H:%M:%S")
        elif len(list(filter(lambda property: property["prop_id"] == "interval.n_intervals", dash.callback_context.triggered))) > 0:
            eventFrameDropdownValue = args[-1]
            # interval n_intervals input fired.
            if eventFrameDropdownValue is not None:
                eventFrame = EventFrame.query.get(eventFrameDropdownValue)
                if eventFrame is not None:
                    if eventFrame.EndTimestamp is not None:
                        raise PreventUpdate

        return fromTimestamp, toTimestamp

    @dashApp.callback(Output(component_id = "collapseExpandButton", component_property = "children"),
        [Input(component_id = "collapseExpandButton", component_property = "n_clicks")],
        [State(component_id = "collapseExpandButton", component_property = "children")])
    def collapseExpandButtonChildren(collapseExpandButtonNClicks, collapseExpandButtonChildren):
        if collapseExpandButtonNClicks == 0:
            raise PreventUpdate
        else:
            if collapseExpandButtonChildren == ["Collapse"]:
                return ["Expand"]
            else:
                return ["Collapse"]

    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def enterpriseDropDownOptions(urlHref):
        return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "value"),
        [Input(component_id = "enterpriseDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def enterpriseDropdownValue(enterpriseDropdownOptions, urlHref):
        enterpriseDropdownValue = None
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if enterpriseDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "enterpriseId" in queryString:
                    enterpriseId = int(queryString["enterpriseId"][0])                
                    if len(list(filter(lambda enterprise: enterprise["value"] == enterpriseId, enterpriseDropdownOptions))) > 0:
                        enterpriseDropdownValue = enterpriseId

        return enterpriseDropdownValue

    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "options"),
        [Input(component_id = "enterpriseDropdown", component_property = "value")])
    def siteDropdownOptions(enterpriseDropdownValue):
        return [{"label": site.Name, "value": site.SiteId} for site in Site.query.filter_by(EnterpriseId = enterpriseDropdownValue). \
            order_by(Site.Name).all()]

    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "value"),
        [Input(component_id = "siteDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def siteDropdownValue(siteDropdownOptions, urlHref):
        siteDropdownValue = None
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if siteDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "siteId" in queryString:
                    siteId = int(queryString["siteId"][0])                
                    if len(list(filter(lambda site: site["value"] == siteId, siteDropdownOptions))) > 0:
                        siteDropdownValue = siteId

        return siteDropdownValue

    @dashApp.callback(Output(component_id = "elementTemplateDropdown", component_property = "options"),
        [Input(component_id = "siteDropdown", component_property = "value")])
    def elementTemplateDropdownOptions(siteDropdownValue):
        return [{"label": elementTemplate.Name, "value": elementTemplate.ElementTemplateId} for elementTemplate in ElementTemplate.query. \
            filter_by(SiteId = siteDropdownValue).order_by(ElementTemplate.Name).all()]

    @dashApp.callback(Output(component_id = "elementTemplateDropdown", component_property = "value"),
        [Input(component_id = "elementTemplateDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def elementTemplateDropdownValue(elementTemplateDropdownOptions, urlHref):
        elementTemplateDropdownValue = None
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if elementTemplateDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "elementTemplateId" in queryString:
                    elementTemplateId = int(queryString["elementTemplateId"][0])                
                    if len(list(filter(lambda elementTemplate: elementTemplate["value"] == elementTemplateId, elementTemplateDropdownOptions))) > 0:
                        elementTemplateDropdownValue = elementTemplateId

        return elementTemplateDropdownValue

    @dashApp.callback(Output(component_id = "eventFrameTemplateDropdown", component_property = "options"),
        [Input(component_id = "elementTemplateDropdown", component_property = "value")])
    def eventFrameTemplateDropdownOptions(elementTemplateDropdownValue):
        return [{"label": eventFrameTemplate.Name, "value": eventFrameTemplate.EventFrameTemplateId} for eventFrameTemplate in EventFrameTemplate.query. \
            filter_by(ElementTemplateId = elementTemplateDropdownValue).order_by(EventFrameTemplate.Name).all()]

    @dashApp.callback(Output(component_id = "eventFrameTemplateDropdown", component_property = "value"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def eventFrameTemplateDropdownValue(eventFrameTemplateDropdownOptions, urlHref):
        eventFrameTemplateDropdownValue = None
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if eventFrameTemplateDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameTemplateId" in queryString:
                    eventFrameTemplateId = int(queryString["eventFrameTemplateId"][0])                
                    if len(list(filter(lambda eventFrameTemplate: eventFrameTemplate["value"] == eventFrameTemplateId,
                        eventFrameTemplateDropdownOptions))) > 0:
                        eventFrameTemplateDropdownValue = eventFrameTemplateId

        return eventFrameTemplateDropdownValue

    @dashApp.callback(Output(component_id = "eventFrameDropdown", component_property = "options"),
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value"),
        Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "url", component_property = "href")])
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

    @dashApp.callback(Output(component_id = "eventFrameDropdown", component_property = "value"),
        [Input(component_id = "eventFrameDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "eventFrameDropdown", component_property = "value")])
    def eventFrameDropdownValue(eventFrameDropdownOptions, urlHref, eventFrameDropdownValue):
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
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

    @dashApp.callback([Output(component_id = "eventFrameTemplateViewDropdown", component_property = "options"),
        Output(component_id = "eventFrameTemplateViewDropdown", component_property = "value")],
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameDropdownOptions(eventFrameTemplateDropdownValue):
        if eventFrameTemplateDropdownValue is None:
            return [[], None]

        eventFrameTemplateViews = [{"label": eventFrameTemplateView.Name, "value": eventFrameTemplateView.EventFrameTemplateViewId}
            for eventFrameTemplateView in EventFrameTemplateView.query.filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue). \
                order_by(EventFrameTemplateView.Name).all()]
        eventFrameTemplateViews.insert(0, {"label": "All", "value": -1})
        return [eventFrameTemplateViews, -1]

    @dashApp.callback([Output(component_id = "graph", component_property = "figure"),
        Output(component_id = "table", component_property = "data")],
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "eventFrameDropdown", component_property = "value"),
        Input(component_id = "eventFrameTemplateViewDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, eventFrameDropdownValue, eventFrameTemplateViewDropdownValue, urlHref, intervalNIntervals,
        refreshButtonNClicks):
        if eventFrameDropdownValue is None:
            return {"data": []}, []

        if fromTimestampInputValue == "" or toTimestampInputValue == "":
            raise PreventUpdate

        eventFrame = EventFrame.query.get(eventFrameDropdownValue)
        data = []
        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
        toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

        for tagValue in eventFrame.tagValues(eventFrameTemplateViewDropdownValue):
            # Search for tag dict in list of dicts.
            listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == tagValue.Tag.Name, data))
            if len(listOfDictionaries) == 0:
                # Tag dict doesn't exist so append it to the list of dicts.
                if tagValue.Tag.LookupId is None:
                    data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                        y = [tagValue.Value],
                        text = [tagValue.Tag.UnitOfMeasurement.Abbreviation],
                        name = tagValue.Tag.Name,
                        mode = "lines+markers"))
                else:
                    data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                        y = [tagValue.Value],
                        text = [LookupValue.query.filter_by(LookupId = tagValue.Tag.LookupId, Value = tagValue.Value).one().Name],
                        name = tagValue.Tag.Name,
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
                listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == "{} Notes".format(tagValue.Tag.Name), data))
                if len(listOfDictionaries) == 0:
                    # Tag notes dict doesn't exist so append it to the list of dicts.
                    data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                        y = [tagValue.Value],
                        text = [tagValueNotes],
                        name = "{} Notes".format(tagValue.Tag.Name),
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
            eventFrameNotes.append({"Timestamp": eventFrameNote.Timestamp.strftime("%Y-%m-%d %H:%M:%S"), "Note": eventFrameNote.Note})

        return {"data": data, "layout": {"shapes": shapes, "uirevision": "{}{}".format(fromTimestampInputValue, toTimestampInputValue)}}, eventFrameNotes

    @dashApp.callback([Output(component_id = "refreshRateButton", component_property = "children"),
        Output(component_id = "interval", component_property = "interval"),
        Output(component_id = "interval", component_property = "disabled")],
        [Input(component_id = "offLi", component_property = "n_clicks"),
        Input(component_id = "fiveSecondLi", component_property = "n_clicks"),
        Input(component_id = "tenSecondLi", component_property = "n_clicks"),
        Input(component_id = "thirtySecondLi", component_property = "n_clicks"),
        Input(component_id = "oneMinuteLi", component_property = "n_clicks"),
        Input(component_id = "fiveMinuteLi", component_property = "n_clicks"),
        Input(component_id = "fifthteenMinuteLi", component_property = "n_clicks"),
        Input(component_id = "thirtyMinuteLi", component_property = "n_clicks"),
        Input(component_id = "oneHourLi", component_property = "n_clicks"),
        Input(component_id = "twoHourLi", component_property = "n_clicks"),
        Input(component_id = "oneDayLi", component_property = "n_clicks")])
    def interval(*args, **kwargs):
        return timestampRangeComponent.intervalCallback(*args, **kwargs)
