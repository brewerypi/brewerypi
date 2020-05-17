import dash
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import parse_qs, urlparse
from app.models import ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, EventFrameTemplateView, Site

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
        return (localNow - relativedelta(months = 3)).strftime("%Y-%m-%dT%H:%M:%S")

    @dashApp.callback(Output(component_id = "toTimestampInput", component_property = "value"),
        [Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals")])
    def toTimestampValues(urlHref, intervalNIntervals):
        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        utcNow = pytz.utc.localize(datetime.utcnow())
        localNow = utcNow.astimezone(localTimezone)
        return localNow.strftime("%Y-%m-%dT%H:%M:%S")

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
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameDropdownOptions(eventFrameTemplateDropdownValue):
        return [{"label": eventFrame.Name, "value": eventFrame.EventFrameId} for eventFrame in EventFrame.query. \
            filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue).order_by(EventFrame.StartTimestamp.desc()).all()]

    @dashApp.callback(Output(component_id = "eventFrameDropdown", component_property = "value"),
        [Input(component_id = "eventFrameDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def eventFrameDropdownValue(eventFrameDropdownOptions, urlHref):
        eventFrameDropdownValue = None
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if eventFrameDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "eventFrameId" in queryString:
                    eventFrameId = int(queryString["eventFrameId"][0])                
                    if len(list(filter(lambda eventFrame: eventFrame["value"] == eventFrameId, eventFrameDropdownOptions))) > 0:
                        eventFrameDropdownValue = eventFrameId

        return eventFrameDropdownValue

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

    @dashApp.callback(Output(component_id = "graph", component_property = "figure"),
        [Input(component_id = "eventFrameDropdown", component_property = "value"),
        Input(component_id = "eventFrameTemplateViewDropdown", component_property = "value")])
    def graphFigure(eventFrameDropdownValue, eventFrameTemplateViewDropdownValue):
        if eventFrameDropdownValue is None:
            return {"data": []}

        eventFrame = EventFrame.query.get(eventFrameDropdownValue)
        data = []
        for tagValue in eventFrame.attributeValues(eventFrameTemplateViewDropdownValue):
            # Search for tag name dict in list of dicts.
            tags = list(filter(lambda tag: tag["name"] == tagValue.Tag.Name, data))
            if len(tags) == 0:
                # Tag name dict doesn't exist so append it to the list of dicts.
                data.append(dict(x = [tagValue.Timestamp],
                    y = [tagValue.Value],
                    name = tagValue.Tag.Name,
                    mode = "lines+markers"))
            else:
                # Tag name dict already exists so append to x and y.
                seriesDict = tags[0]
                seriesDict["x"].append(tagValue.Timestamp)
                seriesDict["y"].append(tagValue.Value)

        return {"data": data}
