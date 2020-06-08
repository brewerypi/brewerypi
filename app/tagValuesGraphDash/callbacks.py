import dash
import pytz
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from app.models import LookupValue, Tag, TagValue
from app.dashes import dropdowns, timestampRangeComponent

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
        [State(component_id = "fromTimestampInput", component_property = "value")])
    def fromTimestampInputValueToTimestampInputValue(urlHref, lastFiveMinutesLiNClicks, lastFifthteenMinutesLiNClicks, lastThirtyMinutesLiNClicks,
            lastOneHourLiNClicks, lastThreeHoursLiNClicks, lastSixHoursLiNClicks, lastTwelveHoursLiNClicks, lastTwentyFourHoursLiNClicks, lastTwoDaysLiNClicks,
            lastThirtyDaysLiNClicks, lastNinetyDaysLiNClicks, lastSixMonthsLiNClicks, lastOneYearLiNClicks, lastTwoYearsLiNClicks, lastFiveYearsLiNClicks,
            yesterdayLiNClicks, lastSevenDaysLiNClicks, dayBeforeYesterdayLiNClicks, thisDayLastWeekLiNClicks, previousWeekLiNClicks, previousMonthLiNClicks,
            previousYearLiNClicks, todayLiNClicks, todaySoFarLiNClicks, thisWeekLiNClicks, thisWeekSoFarLiNClicks, thisMonthLiNClicks, thisMonthSoFarLiNClicks,
            thisYearLiNClicks, thisYearSoFarLiNClicks, intervalNIntervals, fromTimestampInputValue):
        return timestampRangeComponent.rangePickerCallback(urlHref, lastFiveMinutesLiNClicks, lastFifthteenMinutesLiNClicks, lastThirtyMinutesLiNClicks,
            lastOneHourLiNClicks, lastThreeHoursLiNClicks, lastSixHoursLiNClicks, lastTwelveHoursLiNClicks, lastTwentyFourHoursLiNClicks, lastTwoDaysLiNClicks,
            lastThirtyDaysLiNClicks, lastNinetyDaysLiNClicks, lastSixMonthsLiNClicks, lastOneYearLiNClicks, lastTwoYearsLiNClicks, lastFiveYearsLiNClicks,
            yesterdayLiNClicks, lastSevenDaysLiNClicks, dayBeforeYesterdayLiNClicks, thisDayLastWeekLiNClicks, previousWeekLiNClicks, previousMonthLiNClicks,
            previousYearLiNClicks, todayLiNClicks, todaySoFarLiNClicks, thisWeekLiNClicks, thisWeekSoFarLiNClicks, thisMonthLiNClicks, thisMonthSoFarLiNClicks,
            thisYearLiNClicks, thisYearSoFarLiNClicks, intervalNIntervals, fromTimestampInputValue)

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
        return timestampRangeComponent.intervalCallback(offLiNClicks, fiveSecondLiNClicks, tenSecondLiNClicks, thirtySecondLiNClicks, oneMinuteLiNClicks,
            fiveMinuteLiNClicks, fifthteenMinuteLiNClicks, thirtyMinuteLiNClicks, oneHourLiNClicks, twoHourLiNClicks, oneDayLiNClicks)

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

    @dashApp.callback(Output(component_id = "enterprisesDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def enterprisesDropdownOptions(urlHref):
        return dropdowns.enterprisesDropdownOptions(urlHref)

    @dashApp.callback(Output(component_id = "enterprisesDropdown", component_property = "value"),
        [Input(component_id = "enterprisesDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def enterprisesDropdownValues(enterprisesDropdownOptions, urlHref):
        return dropdowns.enterprisesDropdownValues(enterprisesDropdownOptions, urlHref)

    @dashApp.callback(Output(component_id = "sitesDropdown", component_property = "options"),
        [Input(component_id = "enterprisesDropdown", component_property = "value")])
    def sitesDropdownOptions(enterprisesDropdownValues):
        return dropdowns.sitesDropdownOptions(enterprisesDropdownValues)

    @dashApp.callback(Output(component_id = "sitesDropdown", component_property = "value"),
        [Input(component_id = "sitesDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "sitesDropdown", component_property = "value")])
    def sitesDropdownValues(sitesDropdownOptions, urlHref, sitesDropdownValues):
        return dropdowns.sitesDropdownValues(sitesDropdownOptions, urlHref, sitesDropdownValues)

    @dashApp.callback(Output(component_id = "areasDropdown", component_property = "options"),
        [Input(component_id = "sitesDropdown", component_property = "value")])
    def areasDropdownOptions(sitesDropdownValues):
        return dropdowns.areasDropdownOptions(sitesDropdownValues)

    @dashApp.callback(Output(component_id = "areasDropdown", component_property = "value"),
        [Input(component_id = "areasDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "areasDropdown", component_property = "value")])
    def areasDropdownValues(areasDropdownOptions, urlHref, areasDropdownValues):
        return dropdowns.areasDropdownValues(areasDropdownOptions, urlHref, areasDropdownValues)

    @dashApp.callback(Output(component_id = "tagsDropdown", component_property = "options"),
        [Input(component_id = "areasDropdown", component_property = "value")])
    def tagsDropdownOptions(areasDropdownValues):
        return dropdowns.tagsDropdownOptions(areasDropdownValues)

    @dashApp.callback(Output(component_id = "tagsDropdown", component_property = "value"),
        [Input(component_id = "tagsDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "tagsDropdown", component_property = "value")])
    def tagsDropdownValues(tagsDropdownOptions, urlHref, tagsDropdownValues):
        return dropdowns.tagsDropdownValues(tagsDropdownOptions, urlHref, tagsDropdownValues)

    @dashApp.callback(Output(component_id = "graph", component_property = "figure"),
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "tagsDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, tagsDropdownValues, urlHref, intervalNIntervals, refreshButtonNClicks):
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
