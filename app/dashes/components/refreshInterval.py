import dash
import sys
from dash import html
from dash.dependencies import Input, Output

def layout():
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

def callback(dashApp):
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
    def callback(offLiNClicks, fiveSecondLiNClicks, tenSecondLiNClicks, thirtySecondLiNClicks, oneMinuteLiNClicks, fiveMinuteLiNClicks,
        fifthteenMinuteLiNClicks, thirtyMinuteLiNClicks, oneHourLiNClicks, twoHourLiNClicks, oneDayLiNClicks):
        componentId = dash.callback_context.triggered[0]["prop_id"].split(".")[0]
        if componentId == "offLi":
            refreshRateText = "Off"
            refreshRateMilliseconds = sys.maxsize
            disabled = True
        elif componentId == "fiveSecondLi":
            refreshRateText = "5s"
            refreshRateMilliseconds = 5 * 1000
            disabled = False
        elif componentId == "tenSecondLi":
            refreshRateText = "10s"
            refreshRateMilliseconds = 10 * 1000
            disabled = False
        elif componentId == "thirtySecondLi":
            refreshRateText = "30s"
            refreshRateMilliseconds = 30 * 1000
            disabled = False
        elif componentId == "oneMinuteLi":
            refreshRateText = "1m"
            refreshRateMilliseconds = 60 * 1 * 1000
            disabled = False
        elif componentId == "fiveMinuteLi":
            refreshRateText = "5m"
            refreshRateMilliseconds = 60 * 5 * 1000
            disabled = False
        elif componentId == "fifthteenMinuteLi":
            refreshRateText = "15m"
            refreshRateMilliseconds = 60 * 15 * 1000
            disabled = False
        elif componentId == "thirtyMinuteLi":
            refreshRateText = "30m"
            refreshRateMilliseconds = 60 * 30 * 1000
            disabled = False
        elif componentId == "oneHourLi":
            refreshRateText = "1h"
            refreshRateMilliseconds = 60 * 60 * 1 * 1000
            disabled = False
        elif componentId == "twoHourLi":
            refreshRateText = "2h"
            refreshRateMilliseconds = 60 * 60 * 2 * 1000
            disabled = False
        elif componentId == "oneDayLi":
            refreshRateText = "1d"
            refreshRateMilliseconds = 60 * 60 * 24 * 1000
            disabled = False
        else:
            refreshRateText = "Off"
            refreshRateMilliseconds = sys.maxsize
            disabled = True

        return [refreshRateText + " ", html.Span(className = "caret")], refreshRateMilliseconds, disabled
