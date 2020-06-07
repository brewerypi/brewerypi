import dash
import pytz
import sys
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime
from dateutil.relativedelta import calendar, relativedelta
from urllib.parse import parse_qs, urlparse

def intervalCallback(offLiNClicks, fiveSecondLiNClicks, tenSecondLiNClicks, thirtySecondLiNClicks, oneMinuteLiNClicks, fiveMinuteLiNClicks,
    fifthteenMinuteLiNClicks, thirtyMinuteLiNClicks, oneHourLiNClicks, twoHourLiNClicks, oneDayLiNClicks):
    changedId = [property['prop_id'] for property in dash.callback_context.triggered][0]
    if "offLi" in changedId:
        refreshRateText = "Off"
        refreshRateMilliseconds = sys.maxsize
        disabled = True
    elif "fiveSecondLi" in changedId:
        refreshRateText = "5s"
        refreshRateMilliseconds = 5 * 1000
        disabled = False
    elif "tenSecondLi" in changedId:
        refreshRateText = "10s"
        refreshRateMilliseconds = 10 * 1000
        disabled = False
    elif "thirtySecondLi" in changedId:
        refreshRateText = "30s"
        refreshRateMilliseconds = 30 * 1000
        disabled = False
    elif "oneMinuteLi" in changedId:
        refreshRateText = "1m"
        refreshRateMilliseconds = 60 * 1 * 1000
        disabled = False
    elif "fiveMinuteLi" in changedId:
        refreshRateText = "5m"
        refreshRateMilliseconds = 60 * 5 * 1000
        disabled = False
    elif "fifthteenMinuteLi" in changedId:
        refreshRateText = "15m"
        refreshRateMilliseconds = 60 * 15 * 1000
        disabled = False
    elif "thirtyMinuteLi" in changedId:
        refreshRateText = "30m"
        refreshRateMilliseconds = 60 * 30 * 1000
        disabled = False
    elif "oneHourLi" in changedId:
        refreshRateText = "1h"
        refreshRateMilliseconds = 60 * 60 * 1 * 1000
        disabled = False
    elif "twoHourLi" in changedId:
        refreshRateText = "2h"
        refreshRateMilliseconds = 60 * 60 * 2 * 1000
        disabled = False
    elif "oneDayLi" in changedId:
        refreshRateText = "1d"
        refreshRateMilliseconds = 60 * 60 * 24 * 1000
        disabled = False
    else:
        refreshRateText = "Off"
        refreshRateMilliseconds = sys.maxsize
        disabled = True

    return [refreshRateText + " ", html.Span(className = "caret")], refreshRateMilliseconds, disabled

def intervalLayout():
    return html.Div(className = "btn-group", role = "group", children =
    [
        html.Button(id = "refreshRateButton", className = "btn btn-default dropdown-toggle btn-sm", **{"data-toggle": "dropdown",
            "aria-haspopup": "true", "aria-expanded": "false"}, children = ["Off ", html.Span(className = "caret")], title = "Refresh Interval"),
        html.Ul(className = "dropdown-menu", children =
        [
            html.Li(id = "offLi", children = html.A("Off")),
            html.Li(id = "fiveSecondLi", children = html.A("5s")),
            html.Li(id = "tenSecondLi", children = html.A("10s")),
            html.Li(id = "thirtySecondLi", children = html.A("30s")),
            html.Li(id = "oneMinuteLi", children = html.A("1m")),
            html.Li(id = "fiveMinuteLi", children = html.A("5m")),
            html.Li(id = "fifthteenMinuteLi", children = html.A("15m")),
            html.Li(id = "thirtyMinuteLi", children = html.A("30m")),
            html.Li(id = "oneHourLi", children = html.A("1h")),
            html.Li(id = "twoHourLi", children = html.A("2h")),
            html.Li(id = "oneDayLi", children = html.A("1d"))
        ])
    ])

def layout():
    return html.Div(children =
    [
        "From: ", 
        dcc.Input(id = "fromTimestampInput", type = "datetime-local", step = "1"),
        " to: ",
        dcc.Input(id = "toTimestampInput", type = "datetime-local", step = "1"),
        rangePickerLayout(),
        html.Button(id = "refreshButton", className = "btn btn-default btn-sm", children = [html.Span(className = "glyphicon glyphicon-refresh")],
            title = "Refresh"),
        intervalLayout()
    ])

def rangePickerCallback(urlHref, lastFiveMinutesLiNClicks, lastFifthteenMinutesLiNClicks, lastThirtyMinutesLiNClicks, lastOneHourLiNClicks,
    lastThreeHoursLiNClicks, lastSixHoursLiNClicks, lastTwelveHoursLiNClicks, lastTwentyFourHoursLiNClicks, lastTwoDaysLiNClicks, lastThirtyDaysLiNClicks,
    lastNinetyDaysLiNClicks, lastSixMonthsLiNClicks, lastOneYearLiNClicks, lastTwoYearsLiNClicks, lastFiveYearsLiNClicks, yesterdayLiNClicks,
    lastSevenDaysLiNClicks, dayBeforeYesterdayLiNClicks, thisDayLastWeekLiNClicks, previousWeekLiNClicks, previousMonthLiNClicks, previousYearLiNClicks,
    todayLiNClicks, todaySoFarLiNClicks, thisWeekLiNClicks, thisWeekSoFarLiNClicks, thisMonthLiNClicks, thisMonthSoFarLiNClicks, thisYearLiNClicks,
    thisYearSoFarLiNClicks, intervalNIntervals, fromTimestampInputValue):
    queryString = parse_qs(urlparse(urlHref).query)
    if "localTimezone" in queryString:
        localTimezone = pytz.timezone(queryString["localTimezone"][0])
    else:
        localTimezone = pytz.utc

    utcNow = pytz.utc.localize(datetime.utcnow())
    localNow = utcNow.astimezone(localTimezone)
    today = datetime(localNow.year, localNow.month, localNow.day, 0, 0, 0)
    toTimestamp = localNow
    changedId = [property['prop_id'] for property in dash.callback_context.triggered][0]
    if "lastFiveMinutesLi" in changedId:
        fromTimestamp = localNow - relativedelta(minutes = 5)
    elif "lastFifthteenMinutesLi" in changedId:
        fromTimestamp = localNow - relativedelta(minutes = 15)
    elif "lastThirtyMinutesLi" in changedId:
        fromTimestamp = localNow - relativedelta(minutes = 30)
    elif "lastOneHourLi" in changedId:
        fromTimestamp = localNow - relativedelta(hours = 1)
    elif "lastThreeHoursLi" in changedId:
        fromTimestamp = localNow - relativedelta(hours = 3)
    elif "lastSixHoursLi" in changedId:
        fromTimestamp = localNow - relativedelta(hours = 6)
    elif "lastTwelveHoursLi" in changedId:
        fromTimestamp = localNow - relativedelta(hours = 12)
    elif "lastTwentyFourHoursLi" in changedId:
        fromTimestamp = localNow - relativedelta(hours = 24)
    elif "lastTwoDaysLi" in changedId:
        fromTimestamp = localNow - relativedelta(days = 2)
    elif "lastSevenDaysLi" in changedId:
        fromTimestamp = localNow - relativedelta(days = 7)
    elif "lastThirtyDaysLi" in changedId:
        fromTimestamp = localNow - relativedelta(days = 30)
    elif "lastNinetyDaysLi" in changedId:
        fromTimestamp = localNow - relativedelta(days = 90)
    elif "lastSixMonthsLi" in changedId:
        fromTimestamp = localNow - relativedelta(months = 6)
    elif "lastOneYearLi" in changedId:
        fromTimestamp = localNow - relativedelta(years = 1)
    elif "lastTwoYearsLi" in changedId:
        fromTimestamp = localNow - relativedelta(years = 2)
    elif "lastFiveYearsLi" in changedId:
        fromTimestamp = localNow - relativedelta(years = 5)
    elif "yesterdayLi" in changedId:
        fromTimestamp = today - relativedelta(days = 1)
        toTimestamp = today - relativedelta(seconds = 1)
    elif "dayBeforeYesterdayLi" in changedId:
        fromTimestamp = today - relativedelta(days = 2)
        toTimestamp = today - relativedelta(days = 1) - relativedelta(seconds = 1)
    elif "thisDayLastWeekLi" in changedId:
        fromTimestamp = today - relativedelta(weeks = 1)
        toTimestamp = today - relativedelta(days = 6) - relativedelta(seconds = 1)
    elif "previousWeekLi" in changedId:
        oneWeekAgo = today - relativedelta(weeks = 1)
        twoWeeksAgo = today - relativedelta(weeks = 2)
        fromTimestamp = twoWeeksAgo + relativedelta(weekday = calendar.SUNDAY)
        toTimestamp = oneWeekAgo + relativedelta(weekday = calendar.SUNDAY) - relativedelta(seconds = 1)
    elif "previousMonthLi" in changedId:
        oneMonthAgo = today - relativedelta(months = 1)
        fromTimestamp = datetime(oneMonthAgo.year, oneMonthAgo.month, 1, 0, 0, 0)
        toTimestamp = datetime(today.year, today.month, 1, 0, 0, 0) - relativedelta(seconds = 1)
    elif "previousYearLi" in changedId:
        oneYearAgo = today - relativedelta(years = 1)
        fromTimestamp = datetime(oneYearAgo.year, 1, 1, 0, 0, 0)
        toTimestamp = datetime(today.year, 1, 1, 0, 0, 0) - relativedelta(seconds = 1)
    elif "todayLi" in changedId:
        fromTimestamp = today
        toTimestamp = today + relativedelta(days = 1) - relativedelta(seconds = 1)
    elif "todaySoFarLi" in changedId:
        fromTimestamp = today
    elif "thisWeekLi" in changedId:
        oneWeekAgo = today - relativedelta(weeks = 1)
        fromTimestamp = oneWeekAgo + relativedelta(weekday = calendar.SUNDAY)
        toTimestamp = today + relativedelta(weekday = calendar.SUNDAY) - relativedelta(seconds = 1)
    elif "thisWeekSoFarLi" in changedId:
        oneWeekAgo = today - relativedelta(weeks = 1)
        fromTimestamp = oneWeekAgo + relativedelta(weekday = calendar.SUNDAY)
    elif "thisMonthLi" in changedId:
        fromTimestamp = datetime(today.year, today.month, 1, 0, 0, 0)
        oneMonthAhead = today + relativedelta(months = 1)
        toTimestamp = datetime(oneMonthAhead.year, oneMonthAhead.month, 1, 0, 0, 0) - relativedelta(seconds = 1)
    elif "thisMonthSoFarLi" in changedId:
        fromTimestamp = datetime(today.year, today.month, 1, 0, 0, 0)
    elif "thisYearLi" in changedId:
        fromTimestamp = datetime(today.year, 1, 1, 0, 0, 0)
        oneYearAhead = today + relativedelta(years = 1)
        toTimestamp = datetime(oneYearAhead.year, 1, 1, 0, 0, 0) - relativedelta(seconds = 1)
    elif "thisYearSoFarLi" in changedId:
        fromTimestamp = datetime(today.year, 1, 1, 0, 0, 0)
    elif "interval" in changedId:
        fromTimestamp = datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S")
    else:
        fromTimestamp = (localNow - relativedelta(months = 3))

    return fromTimestamp.strftime("%Y-%m-%dT%H:%M:%S"), toTimestamp.strftime("%Y-%m-%dT%H:%M:%S")

def rangePickerLayout():
    return html.Div(className = "btn-group", role = "group", children =
    [
        html.Button(id = "timestampRangePickerButton", className = "btn btn-default dropdown-toggle btn-sm", **{"data-toggle": "dropdown",
            "aria-haspopup": "true", "aria-expanded": "false"}, children = ["Quick time range"]),
        html.Ul(className = "dropdown-menu", children =
        [
            html.Li(id = "lastFiveMinutesLi", children = html.A("Last 5 minutes")),
            html.Li(id = "lastFifthteenMinutesLi", children = html.A("Last 15 minutes")),
            html.Li(id = "lastThirtyMinutesLi", children = html.A("Last 30 minutes")),
            html.Li(id = "lastOneHourLi", children = html.A("Last 1 hour")),
            html.Li(id = "lastThreeHoursLi", children = html.A("Last 3 hours")),
            html.Li(id = "lastSixHoursLi", children = html.A("Last 6 hours")),
            html.Li(id = "lastTwelveHoursLi", children = html.A("Last 12 hours")),
            html.Li(id = "lastTwentyFourHoursLi", children = html.A("Last 24 hours")),
            html.Li(id = "lastTwoDaysLi", children = html.A("Last 2 days")),
            html.Li(id = "lastSevenDaysLi", children = html.A("Last 7 days")),
            html.Li(id = "lastThirtyDaysLi", children = html.A("Last 30 days")),
            html.Li(id = "lastNinetyDaysLi", children = html.A("Last 90 days")),
            html.Li(id = "lastSixMonthsLi", children = html.A("Last 6 months")),
            html.Li(id = "lastOneYearLi", children = html.A("Last 1 year")),
            html.Li(id = "lastTwoYearsLi", children = html.A("Last 2 years")),
            html.Li(id = "lastFiveYearsLi", children = html.A("Last 5 years")),
            html.Li(id = "yesterdayLi", children = html.A("Yesterday")),
            html.Li(id = "dayBeforeYesterdayLi", children = html.A("Day before yesterday")),
            html.Li(id = "thisDayLastWeekLi", children = html.A("This day last week")),
            html.Li(id = "previousWeekLi", children = html.A("Previous week")),
            html.Li(id = "previousMonthLi", children = html.A("Previous month")),
            html.Li(id = "previousYearLi", children = html.A("Previous year")),
            html.Li(id = "todayLi", children = html.A("Today")),
            html.Li(id = "todaySoFarLi", children = html.A("Today so far")),
            html.Li(id = "thisWeekLi", children = html.A("This week")),
            html.Li(id = "thisWeekSoFarLi", children = html.A("This week so far")),
            html.Li(id = "thisMonthLi", children = html.A("This month")),
            html.Li(id = "thisMonthSoFarLi", children = html.A("This month so far")),
            html.Li(id = "thisYearLi", children = html.A("This year")),
            html.Li(id = "thisYearSoFarLi", children = html.A("This year so far"))
        ])
    ])
