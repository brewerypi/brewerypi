import dash
import dash_html_components as html
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import parse_qs, urlparse
from app.models import Area, Enterprise, LookupValue, Site, Tag, TagValue, TagValueNote

def registerCallbacks(dashApp):
    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def enterpriseDropDownOptions(urlHref):
        return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

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

    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "value"),
        [Input(component_id = "enterpriseDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def enterpriseDropdownValue(enterpriseDropdownOptions, urlHref):
        enterpriseDropdownValues = []
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if enterpriseDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "enterpriseId" in queryString:
                    for urlHrefEnterpriseId in map(int, queryString["enterpriseId"]):
                        if len(list(filter(lambda enterprise: enterprise["value"] == urlHrefEnterpriseId, enterpriseDropdownOptions))) > 0:
                            enterpriseDropdownValues.append(urlHrefEnterpriseId)

        return enterpriseDropdownValues

    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "options"),
        [Input(component_id = "enterpriseDropdown", component_property = "value")])
    def siteDropdownOptions(enterpriseDropdownValues):
        return [{"label": "{}_{}".format(site.Enterprise.Abbreviation, site.Name), "value": site.SiteId} for site in 
            Site.query.join(Enterprise).filter(Site.EnterpriseId.in_(enterpriseDropdownValues)).order_by(Enterprise.Abbreviation, Site.Name).all()]

    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "value"),
        [Input(component_id = "siteDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "siteDropdown", component_property = "value")])
    def siteDropdownValue(siteDropdownOptions, urlHref, siteDropdownSelectedValues):
        if siteDropdownSelectedValues is None:
            siteDropdownValues = []
        else:
            siteDropdownValues = siteDropdownSelectedValues

        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if siteDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "siteId" in queryString:
                    urlHrefSiteId = int(queryString["siteId"][0])
                    for urlHrefSiteId in map(int, queryString["siteId"]):
                        if len(list(filter(lambda site: site["value"] == urlHrefSiteId, siteDropdownOptions))) > 0:
                            siteDropdownValues.append(urlHrefSiteId)

        return siteDropdownValues

    @dashApp.callback(Output(component_id = "areaDropdown", component_property = "options"),
        [Input(component_id = "siteDropdown", component_property = "value")])
    def areaDropdownOptions(siteDropdownValues):
        return [{"label": "{}_{}_{}".format(area.Site.Enterprise.Abbreviation, area.Site.Abbreviation, area.Name), "value": area.AreaId} for area in 
            Area.query.join(Site, Enterprise).filter(Area.SiteId.in_(siteDropdownValues)). \
            order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Name).all()]

    @dashApp.callback(Output(component_id = "areaDropdown", component_property = "value"),
        [Input(component_id = "areaDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "areaDropdown", component_property = "value")])
    def areaDropdownValue(areaDropdownOptions, urlHref, areaDropdownSelectedValues):
        if areaDropdownSelectedValues is None:
            areaDropdownValues = []
        else:
            areaDropdownValues = areaDropdownSelectedValues

        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if areaDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "areaId" in queryString:
                    urlHrefAreaId = int(queryString["areaId"][0])
                    for urlHrefAreaId in map(int, queryString["areaId"]):
                        if len(list(filter(lambda area: area["value"] == urlHrefAreaId, areaDropdownOptions))) > 0:
                            areaDropdownValues.append(urlHrefAreaId)

        return areaDropdownValues

    @dashApp.callback(Output(component_id = "tagDropdown", component_property = "options"),
        [Input(component_id = "areaDropdown", component_property = "value")])
    def tagDropdownOptions(areaDropdownValues):
        return [{"label": "{}_{}_{}_{}".format(tag.Area.Site.Enterprise.Abbreviation, tag.Area.Site.Abbreviation, tag.Area.Abbreviation, tag.Name),
            "value": tag.TagId} for tag in Tag.query.join(Area, Site, Enterprise).filter(Tag.AreaId.in_(areaDropdownValues)).\
            order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name).all()]

    @dashApp.callback(Output(component_id = "tagDropdown", component_property = "value"),
        [Input(component_id = "tagDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "tagDropdown", component_property = "value")])
    def tagDropdownValue(tagDropdownOptions, urlHref, tagDropdownSelectedValues):
        if tagDropdownSelectedValues is None:
            tagDropdownValues = []
        else:
            tagDropdownValues = tagDropdownSelectedValues

        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if tagDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "tagId" in queryString:
                    urlHrefTagId = int(queryString["tagId"][0])
                    for urlHrefTagId in map(int, queryString["tagId"]):
                        if len(list(filter(lambda tag: tag["value"] == urlHrefTagId, tagDropdownOptions))) > 0:
                            tagDropdownValues.append(urlHrefTagId)

        return tagDropdownValues

    @dashApp.callback(Output(component_id = "graph", component_property = "figure"),
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "tagDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, tagDropdownValues, urlHref, intervalNIntervals, refreshButtonNClicks):
        if fromTimestampInputValue is None or toTimestampInputValue is None or tagDropdownValues is None:
            raise PreventUpdate
        else:
            data = []
            if fromTimestampInputValue!= "" and toTimestampInputValue != "" and tagDropdownValues is not None:
                queryString = parse_qs(urlparse(urlHref).query)
                if "localTimezone" in queryString:
                    localTimezone = pytz.timezone(queryString["localTimezone"][0])
                else:
                    localTimezone = pytz.utc

                fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
                toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

                for tagId in tagDropdownValues:
                    tag = Tag.query.get(tagId)
                    tagValues = TagValue.query.filter(TagValue.TagId == tag.TagId, TagValue.Timestamp >= fromTimestampUtc, TagValue.Timestamp <= toTimestampUtc)
                    tagValueNotes = TagValueNote.query.join(TagValue).filter(TagValue.TagId == tagId, TagValue.Timestamp >= fromTimestampUtc,
                        TagValue.Timestamp <= toTimestampUtc).all()

                    if tag.LookupId is None:
                        data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone) for tagValue in tagValues],
                            y = [tagValue.Value for tagValue in tagValues],
                            text = [tagValue.Tag.UnitOfMeasurement.Abbreviation for tagValue in tagValues],
                            name = tag.Name,
                            mode = "lines+markers"))
                    else:
                        data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone) for tagValue in tagValues],
                            y = [tagValue.Value for tagValue in tagValues],
                            text = [LookupValue.query.filter_by(LookupId = tag.LookupId, Value = tagValue.Value).one().Name for tagValue in tagValues],
                            name = tag.Name,
                            mode = "lines+markers"))

                    if len(tagValueNotes) > 0:
                        data.append(dict(x = [pytz.utc.localize(tagValueNote.TagValue.Timestamp).astimezone(localTimezone) for tagValueNote in tagValueNotes],
                            y = [tagValueNote.TagValue.Value for tagValueNote in tagValueNotes],
                            text = ["{}: {}".format(pytz.utc.localize(tagValueNote.Note.Timestamp).astimezone(localTimezone), tagValueNote.Note.Note)
                                for tagValueNote in tagValueNotes],
                            name = "{} Notes".format(tag.Name),
                            mode = "markers"))

            return {"data": data, "layout": {"uirevision": "{}{}".format(fromTimestampInputValue, toTimestampInputValue)}}

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
