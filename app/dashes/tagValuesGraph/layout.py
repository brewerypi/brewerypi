from dash import dcc
from dash import html
from app.dashes.components import areasDropdown, collapseExpand, enterprisesDropdown, sitesDropdown, tagsDropdown, timeRangePicker

layout = html.Div(children =
[
    html.Div(id = "loadingDiv", className = "text-center", children = [html.Img(src = "/static/images/loading.gif")]),
    dcc.Location(id = "url"),
    dcc.Interval(id = "interval", n_intervals = 0, disabled = True),
    html.Div(id = "dashDiv", style = {"display": "none"}, children =
    [
        timeRangePicker.layout(),
        html.Br(),
        collapseExpand.layout(
        [
            enterprisesDropdown.layout(),
            sitesDropdown.layout(),
            areasDropdown.layout(),
            tagsDropdown.layout()
        ]),
        html.Div(children = [dcc.Graph(id = "graph")])
    ])
])
