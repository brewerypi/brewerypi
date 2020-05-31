import dash
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import parse_qs, urlparse
from app.models import Area, Enterprise, LookupValue, Site, Tag, TagValue, TagValueNote
from app.dashes import helpers

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
        return (localNow - relativedelta(months = 3)).strftime("%Y-%m-%dT%H:%M")

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
        return localNow.strftime("%Y-%m-%dT%H:%M")

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
        enterpriseDropdownValues = []
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if enterpriseDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "enterpriseId" in queryString:
                    for enterpriseId in map(int, queryString["enterpriseId"]):
                        if len(list(filter(lambda enterprise: enterprise["value"] == enterpriseId, enterpriseDropdownOptions))) > 0:
                            enterpriseDropdownValues.append(enterpriseId)

        return enterpriseDropdownValues

    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "options"),
        [Input(component_id = "enterpriseDropdown", component_property = "value")])
    def siteDropdownOptions(enterpriseDropdownValues):
        return [{"label": "{}_{}".format(site.Enterprise.Abbreviation, site.Name), "value": site.SiteId} for site in 
            Site.query.join(Enterprise).filter(Site.EnterpriseId.in_(enterpriseDropdownValues)).order_by(Enterprise.Abbreviation, Site.Name).all()]

    @dashApp.callback(Output(component_id = "siteDropdown", component_property = "value"),
        [Input(component_id = "siteDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def siteDropdownValue(siteDropdownOptions, urlHref):
        siteDropdownValues = []
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if siteDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "siteId" in queryString:
                    for siteId in map(int, queryString["siteId"]):
                        if len(list(filter(lambda site: site["value"] == siteId, siteDropdownOptions))) > 0:
                            siteDropdownValues.append(siteId)

        return siteDropdownValues

    @dashApp.callback(Output(component_id = "areaDropdown", component_property = "options"),
        [Input(component_id = "siteDropdown", component_property = "value")])
    def areaDropdownOptions(siteDropdownValues):
        return [{"label": "{}_{}_{}".format(area.Site.Enterprise.Abbreviation, area.Site.Abbreviation, area.Name), "value": area.AreaId} for area in 
            Area.query.join(Site, Enterprise).filter(Area.SiteId.in_(siteDropdownValues)). \
            order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Name).all()]

    @dashApp.callback(Output(component_id = "areaDropdown", component_property = "value"),
        [Input(component_id = "areaDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def areaDropdownValue(areaDropdownOptions, urlHref):
        areaDropdownValues = []
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if areaDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "areaId" in queryString:
                    for areaId in map(int, queryString["areaId"]):
                        if len(list(filter(lambda area: area["value"] == areaId, areaDropdownOptions))) > 0:
                            areaDropdownValues.append(areaId)

        return areaDropdownValues

    @dashApp.callback(Output(component_id = "tagDropdown", component_property = "options"),
        [Input(component_id = "areaDropdown", component_property = "value")])
    def tagDropdownOptions(areaDropdownValues):
        return [{"label": "{}_{}_{}_{}".format(tag.Area.Site.Enterprise.Abbreviation, tag.Area.Site.Abbreviation, tag.Area.Abbreviation, tag.Name),
            "value": tag.TagId} for tag in Tag.query.join(Area, Site, Enterprise).filter(Tag.AreaId.in_(areaDropdownValues)).\
            order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name).all()]

    @dashApp.callback(Output(component_id = "tagDropdown", component_property = "value"),
        [Input(component_id = "tagDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def tagDropdownValue(tagDropdownOptions, urlHref):
        tagDropdownValues = []
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if tagDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "tagId" in queryString:
                    for tagId in map(int, queryString["tagId"]):
                        if len(list(filter(lambda tag: tag["value"] == tagId, tagDropdownOptions))) > 0:
                            tagDropdownValues.append(tagId)

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

                fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M"))
                toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M"))
                fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
                toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

                for tagId in tagDropdownValues:
                    tag = Tag.query.get(tagId)
                    tagValues = TagValue.query.filter(TagValue.TagId == tag.TagId, TagValue.Timestamp >= fromTimestampUtc, TagValue.Timestamp <= toTimestampUtc)
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

                    for tagValue in tagValues:
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
    def interval(*args, **kwargs):
        return helpers.interval(*args, **kwargs)
