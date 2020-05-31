import dash
import dash_html_components as html

def intervalLayout():
    return html.Div(className = "btn-group", role = "group", children =
    [
        html.Div(className = "btn-group", role = "group", children =
        [
            html.Button(id = "refreshRateButton", className = "btn btn-default dropdown-toggle btn-sm", **{"data-toggle": "dropdown",
                "aria-haspopup": "true", "aria-expanded": "false"}, children = ["Off ", html.Span(className = "caret")]),
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
    ])

def intervalCallback(offLiNClicks, fiveSecondLiNClicks, tenSecondLiNClicks, thirtySecondLiNClicks, oneMinuteLiNClicks, fiveMinuteLiNClicks,
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
