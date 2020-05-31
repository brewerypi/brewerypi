import dash
import dash_html_components as html

def interval(offLiNClicks, fiveSecondLiNClicks, tenSecondLiNClicks, thirtySecondLiNClicks, oneMinuteLiNClicks, fiveMinuteLiNClicks,
    fifthteenMinuteLiNClicks, thirtyMinuteLiNClicks, oneHourLiNClicks, twoHourLiNClicks, oneDayLiNClicks):
    changedId = [property['prop_id'] for property in dash.callback_context.triggered][0]
    if "offLiNClicks" in changedId:
        refreshRateText = "Off"
        disabled = True
    elif "fiveSecondLi" in changedId:
        refreshRateText = "5s"
        refreshRateSeconds = 1000 * 5
        disabled = False
    elif "tenSecondLi" in changedId:
        refreshRateText = "10s"
        refreshRateSeconds = 1000 * 10
        disabled = False
    elif "thirtySecondLi" in changedId:
        refreshRateText = "30s"
        refreshRateSeconds = 1000 * 30
        disabled = False
    elif "oneMinuteLi" in changedId:
        refreshRateText = "1m"
        refreshRateSeconds = 1000 * 60
        disabled = False
    elif "fiveMinuteLi" in changedId:
        refreshRateText = "5m"
        refreshRateSeconds = 1000 * 60 * 5
        disabled = False
    elif "fifthteenMinuteLi" in changedId:
        refreshRateText = "15m"
        refreshRateSeconds = 1000 * 60 * 15
        disabled = False
    elif "thirtyMinuteLi" in changedId:
        refreshRateText = "30m"
        refreshRateSeconds = 1000 * 60 * 30
        disabled = False
    elif "oneHourLi" in changedId:
        refreshRateText = "1h"
        refreshRateSeconds = 1000 * 60 * 60
        disabled = False
    elif "twoHourLi" in changedId:
        refreshRateText = "2h"
        refreshRateSeconds = 1000 * 60 * 60 * 2
        disabled = False
    elif "oneDayLi" in changedId:
        refreshRateText = "1d"
        refreshRateSeconds = 1000 * 60 * 60 * 24
        disabled = False
    else:
        refreshRateText = "Off"
        refreshRateSeconds = 1000
        disabled = True

    return [refreshRateText + " ", html.Span(className = "caret")], refreshRateSeconds, disabled
