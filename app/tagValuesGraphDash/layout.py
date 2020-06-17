import dash_core_components as dcc
import dash_html_components as html
from app.dashes.components import areasDropdown, collapseExpandButton, enterprisesDropdown, sitesDropdown, tagsDropdown, timeRangePicker

layout = html.Div(children =
[
    dcc.Location(id = "url"),
    dcc.Interval(id = "interval", n_intervals = 0, disabled = True),
    html.Div(className = "page-header", children = [html.H1("Tag Values Graph")]),
    timeRangePicker.layout(),
    html.Br(),
    collapseExpandButton.layout("dropdownDiv"),
    html.Div(id = "dropdownDiv", className = "collapse in", children =
    [
        html.Div(className = "well well-sm", children =
        [
            enterprisesDropdown.layout(),
            sitesDropdown.layout(),
            areasDropdown.layout(),
            tagsDropdown.layout()
        ])
    ]),
    html.Div(children = [dcc.Graph(id = "graph")]),
])
