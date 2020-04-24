import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from dateutil.relativedelta import relativedelta
from urllib.parse import parse_qs, urlparse
from app.models import Area, Enterprise, LookupValue, Site, Tag, TagValue, TagValueNote

def registerCallbacks(dashApp):
    @dashApp.callback([Output(component_id = "fromTimestampInput", component_property = "value"),
        Output(component_id = "toTimestampInput", component_property = "value"),
        Output(component_id = "enterprisesDropdown", component_property = "options")],
        [Input(component_id = "url", component_property = "href")])
    def initialize(urlHref):
        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        utcNow = pytz.utc.localize(datetime.utcnow())
        localNow = utcNow.astimezone(localTimezone)
        enterpriseOptions = [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]
        return (localNow - relativedelta(months = 3)).strftime("%Y-%m-%dT%H:%M:%S"), localNow.strftime("%Y-%m-%dT%H:%M:%S"), enterpriseOptions

    @dashApp.callback(Output(component_id = "enterprisesDropdown", component_property = "value"),
        [Input(component_id = "enterprisesDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def enterprisesDropdownValue(enterprisesDropdownOptions, urlHref):
        if enterprisesDropdownOptions is None:
            raise PreventUpdate
        else:
            queryString = parse_qs(urlparse(urlHref).query)
            if "enterpriseId" in queryString:
                return [int(queryString["enterpriseId"][0])]
            else:
                return [enterprisesDropdownOptions[0]["value"]]

    @dashApp.callback(Output(component_id = "sitesDropdown", component_property = "options"),
        [Input(component_id = "enterprisesDropdown", component_property = "value")])
    def sitesDropdownOptions(enterprisesDropdownValues):
        if enterprisesDropdownValues is None:
            raise PreventUpdate
        else:
            return [{"label": "{}_{}".format(site.Enterprise.Abbreviation, site.Name), "value": site.SiteId} for site in 
                Site.query.join(Enterprise).filter(Site.EnterpriseId.in_(enterprisesDropdownValues)).order_by(Enterprise.Abbreviation, Site.Name).all()]

    @dashApp.callback(Output(component_id = "sitesDropdown", component_property = "value"),
        [Input(component_id = "sitesDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "sitesDropdown", component_property = "value")])
    def sitesDropdownValue(sitesDropdownOptions, urlHref, sitesDropdownSelectedValues):
        if sitesDropdownSelectedValues is None:
            queryString = parse_qs(urlparse(urlHref).query)
            if "siteId" in queryString:
                return [int(queryString["siteId"][0])]
            else:
                raise PreventUpdate
        else:
            return list(set([sitesDropdownOption["value"] for sitesDropdownOption in sitesDropdownOptions]) & set(sitesDropdownSelectedValues))

    @dashApp.callback(Output(component_id = "areasDropdown", component_property = "options"),
        [Input(component_id = "sitesDropdown", component_property = "value")])
    def areasDropdownOptions(sitesDropdownValues):
        if sitesDropdownValues is None:
            raise PreventUpdate
        else:
            return [{"label": "{}_{}_{}".format(area.Site.Enterprise.Abbreviation, area.Site.Abbreviation, area.Name), "value": area.AreaId} for area in 
                Area.query.join(Site, Enterprise).filter(Area.SiteId.in_(sitesDropdownValues)). \
                order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Name).all()]

    @dashApp.callback(Output(component_id = "areasDropdown", component_property = "value"),
        [Input(component_id = "areasDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "areasDropdown", component_property = "value")])
    def areasDropdownValue(areasDropdownOptions, urlHref, areasDropdownSelectedValues):
        if areasDropdownSelectedValues is None:
            queryString = parse_qs(urlparse(urlHref).query)
            if "areaId" in queryString:
                return [int(queryString["areaId"][0])]
            else:
                raise PreventUpdate
        else:
            return list(set([areasDropdownOption["value"] for areasDropdownOption in areasDropdownOptions]) & set(areasDropdownSelectedValues))

    @dashApp.callback(Output(component_id = "tagsDropdown", component_property = "options"),
        [Input(component_id = "areasDropdown", component_property = "value")])
    def tagsDropdownOptions(areasDropdownValues):
        if areasDropdownValues is None:
            raise PreventUpdate
        else:
            return [{"label": "{}_{}_{}_{}".format(tag.Area.Site.Enterprise.Abbreviation, tag.Area.Site.Abbreviation, tag.Area.Abbreviation, tag.Name),
                "value": tag.TagId} for tag in Tag.query.join(Area, Site, Enterprise).filter(Tag.AreaId.in_(areasDropdownValues)).\
                order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name).all()]

    @dashApp.callback(Output(component_id = "tagsDropdown", component_property = "value"),
        [Input(component_id = "tagsDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "tagsDropdown", component_property = "value")])
    def tagsDropdownValue(tagsDropdownOptions, urlHref, tagsDropdownSelectedValues):
        if tagsDropdownSelectedValues is None:
            queryString = parse_qs(urlparse(urlHref).query)
            if "tagId" in queryString:
                return [int(queryString["tagId"][0])]
            else:
                raise PreventUpdate
        else:
            return list(set([tagsDropdownOption["value"] for tagsDropdownOption in tagsDropdownOptions]) & set(tagsDropdownSelectedValues))

    @dashApp.callback(Output(component_id = "graph", component_property = "figure"),
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "tagsDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href")])
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, tagsDropdownValues, urlHref):
        if fromTimestampInputValue is None or toTimestampInputValue is None or tagsDropdownValues is None:
            raise PreventUpdate
        else:
            data = []
            if fromTimestampInputValue!= "" and toTimestampInputValue != "" and tagsDropdownValues is not None:
                queryString = parse_qs(urlparse(urlHref).query)
                if "localTimezone" in queryString:
                    localTimezone = pytz.timezone(queryString["localTimezone"][0])
                else:
                    localTimezone = pytz.utc

                fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
                toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

                for tagId in tagsDropdownValues:
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

            return {"data": data}
