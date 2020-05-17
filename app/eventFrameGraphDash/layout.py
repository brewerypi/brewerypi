import dash_core_components as dcc
import dash_html_components as html

layout = html.Div(children =
[
    dcc.Location(id = "url"),
    dcc.Interval(id = "interval", n_intervals = 0, disabled = True),
    html.Div(className = "page-header", children = [html.H1("Event Frame Graph")]),
    html.Div(children =
    [
        "From: ", 
        dcc.Input(id = "fromTimestampInput", type = "datetime-local"),
        " to: ",
        dcc.Input(id = "toTimestampInput", type = "datetime-local"),
        html.Button(id  = "refreshButton", children = [html.Span(className = "glyphicon glyphicon-refresh")]),
        html.Div(className = "btn-group", role = "group", children =
        [
            html.Div(className = "btn-group", role = "group",
            children =
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
    ]),
    html.Br(),
    html.Div(children =
    [
        dcc.Dropdown(id = "enterpriseDropdown", placeholder = "Select Enterprise", multi = False),
        dcc.Dropdown(id = "siteDropdown", placeholder = "Select Site", multi = False),
        dcc.Dropdown(id = "elementTemplateDropdown", placeholder = "Select Element Template", multi = False),
        dcc.Dropdown(id = "eventFrameTemplateDropdown", placeholder = "Select Event Frame Template", multi = False),
        dcc.Dropdown(id = "eventFrameDropdown", placeholder = "Select Event Frame", multi = False),
        dcc.Dropdown(id = "eventFrameTemplateViewDropdown", placeholder = "Select View", multi = False)
    ]),
    dcc.Graph(id = "graph")
])
