import dash
import dash_html_components as html
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from sqlalchemy import or_
from urllib.parse import parse_qs, urlparse
from app.models import ElementTemplate, Enterprise, EventFrame, EventFrameNote, EventFrameTemplate, EventFrameTemplateView, LookupValue, Note, Site

def registerCallbacks(dashApp):
    @dashApp.callback(Output(component_id = "fromTimestampInput", component_property = "value"),
        [Input(component_id = "url", component_property = "href")])
    def fromTimestampValue(urlHref):
        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        utcNow = pytz.utc.localize(datetime.utcnow())
        localNow = utcNow.astimezone(localTimezone)
        timestamp = (localNow - relativedelta(months = 3)).strftime("%Y-%m-%dT%H:%M")
        if "eventFrameId" in queryString:
            eventFrameId = int(queryString["eventFrameId"][0])
            eventFrame = EventFrame.query.get(eventFrameId)
            if eventFrame is not None:
                timestamp = eventFrame.StartTimestamp.strftime("%Y-%m-%dT%H:%M")

        return timestamp

    @dashApp.callback(Output(component_id = "toTimestampInput", component_property = "value"),
        [Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals")],
        [State(component_id = "eventFrameDropdown", component_property = "value")])
    def toTimestampValues(urlHref, intervalNIntervals, eventFrameDropdownValue):
        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        utcNow = pytz.utc.localize(datetime.utcnow())
        localNow = utcNow.astimezone(localTimezone)
        timestamp = localNow.strftime("%Y-%m-%dT%H:%M")
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            # url href input fired.
            if "eventFrameId" in queryString:
                eventFrameId = int(queryString["eventFrameId"][0])
                eventFrame = EventFrame.query.get(eventFrameId)
                if eventFrame is not None:
                    if eventFrame.EndTimestamp is not None:
                        # A closed event frame exists so use the end timestamp.
                        timestamp = (eventFrame.EndTimestamp + relativedelta(minutes = 1)).strftime("%Y-%m-%dT%H:%M")
        else:
            # interval n_intervals input fired.
            if eventFrameDropdownValue is not None:
                eventFrame = EventFrame.query.get(eventFrameDropdownValue)
                if eventFrame is not None:
                    if eventFrame.EndTimestamp is not None:
                        raise PreventUpdate

        return timestamp

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

        fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M"))
        toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M"))
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
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, eventFrameDropdownValue, eventFrameTemplateViewDropdownValue, urlHref, intervalNIntervals, refreshButtonNClicks):
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

        fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M"))
        toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M"))
        fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
        toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

        for attributeValue in eventFrame.attributeValues(eventFrameTemplateViewDropdownValue):
            # Search for tag name dict in list of dicts.
            tags = list(filter(lambda tag: tag["name"] == attributeValue.Tag.Name, data))
            if len(tags) == 0:
                # Tag name dict doesn't exist so append it to the list of dicts.
                if attributeValue.Tag.LookupId is None:
                    data.append(dict(x = [pytz.utc.localize(attributeValue.Timestamp).astimezone(localTimezone)],
                        y = [attributeValue.Value],
                        text = [attributeValue.Tag.UnitOfMeasurement.Abbreviation],
                        name = attributeValue.Tag.Name,
                        mode = "lines+markers"))
                else:
                    data.append(dict(x = [pytz.utc.localize(attributeValue.Timestamp).astimezone(localTimezone)],
                        y = [attributeValue.Value],
                        text = [LookupValue.query.filter_by(LookupId = attributeValue.Tag.LookupId, Value = attributeValue.Value).one().Name],
                        name = attributeValue.Tag.Name,
                        mode = "lines+markers"))
            else:
                # Tag name dict already exists so append to x and y.
                seriesDict = tags[0]
                seriesDict["x"].append(pytz.utc.localize(attributeValue.Timestamp).astimezone(localTimezone))
                seriesDict["y"].append(attributeValue.Value)
                if attributeValue.Tag.LookupId is None:
                    seriesDict["text"].append(attributeValue.Tag.UnitOfMeasurement.Abbreviation)
                else:
                    seriesDict["text"].append(LookupValue.query.filter_by(LookupId = attributeValue.Tag.LookupId, Value = attributeValue.Value).one().Name)

        eventFrameStartTimestamp = pytz.utc.localize(eventFrame.StartTimestamp).astimezone(localTimezone)
        shapes = [dict(type = "line", yref = "paper", y0 = 0, y1 = 1, x0 = eventFrameStartTimestamp, x1 = eventFrameStartTimestamp, line =
            dict(width = 1, dash = "dot"))]
        if eventFrame.EndTimestamp is not None:
            eventFrameEndTimestamp = pytz.utc.localize(eventFrame.EndTimestamp).astimezone(localTimezone)
            shapes.append(dict(type = "line", yref = "paper", y0 = 0, y1 = 1, x0 = eventFrameEndTimestamp, x1 = eventFrameEndTimestamp,
                line = dict(width = 1, dash = "dot")))

        notes = []
        eventFrameNotes = Note.query.join(EventFrameNote).filter(EventFrameNote.EventFrameId == eventFrame.EventFrameId).order_by(Note.Timestamp)
        for eventFrameNote in eventFrameNotes:
            notes.append({"Timestamp": eventFrameNote.Timestamp.strftime("%Y-%m-%d %H:%M:%S"), "Note": eventFrameNote.Note})

        return {"data": data, "layout": {"shapes": shapes, "uirevision": "{}{}".format(fromTimestampInputValue, toTimestampInputValue)}}, notes

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
    def interval(offLiNClicks, fiveSecondLiNClicks, tenSecondLiNClicks, thirtySecondLiNClicks, oneMinuteLiNClicks, fiveMinuteLiNClicks,
        fifthteenMinuteLiNClicks, thirtyMinuteLiNClicks, oneHourLiNClicks, twoHourLiNClicks, oneDayLiNClicks):
        changedId = [property['prop_id'] for property in dash.callback_context.triggered][0]
        if "offLiNClicks" in changedId:
            refreshRateText = "Off"
            disabled = True
        elif "fiveSecondLi" in changedId:
            refreshRateText = "5s "
            refreshRateSeconds = 1000 * 5
            disabled = False
        elif "tenSecondLi" in changedId:
            refreshRateText = "10s "
            refreshRateSeconds = 1000 * 10
            disabled = False
        elif "thirtySecondLi" in changedId:
            refreshRateText = "30s "
            refreshRateSeconds = 1000 * 30
            disabled = False
        elif "oneMinuteLi" in changedId:
            refreshRateText = "1m "
            refreshRateSeconds = 1000 * 60
            disabled = False
        elif "fiveMinuteLi" in changedId:
            refreshRateText = "5m "
            refreshRateSeconds = 1000 * 60 * 5
            disabled = False
        elif "fifthteenMinuteLi" in changedId:
            refreshRateText = "15m "
            refreshRateSeconds = 1000 * 60 * 15
            disabled = False
        elif "thirtyMinuteLi" in changedId:
            refreshRateText = "30m "
            refreshRateSeconds = 1000 * 60 * 30
            disabled = False
        elif "oneHourLi" in changedId:
            refreshRateText = "1h "
            refreshRateSeconds = 1000 * 60 * 60
            disabled = False
        elif "twoHourLi" in changedId:
            refreshRateText = "2h "
            refreshRateSeconds = 1000 * 60 * 60 * 2
            disabled = False
        elif "oneDayLi" in changedId:
            refreshRateText = "1d "
            refreshRateSeconds = 1000 * 60 * 60 * 24
            disabled = False
        else:
            refreshRateText = "Off"
            refreshRateSeconds = 1000
            disabled = True

        return [refreshRateText, html.Span(className = "caret")], refreshRateSeconds, disabled
