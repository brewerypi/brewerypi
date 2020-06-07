import dash_core_components as dcc
import dash_html_components as html
from app.dashes import dropdowns, timestampRangeComponent

layout = html.Div(children =
[
    dcc.Location(id = "url"),
    dcc.Interval(id = "interval", n_intervals = 0, disabled = True),
    html.Div(className = "page-header", children = [html.H1("Tag Values Graph")]),
    timestampRangeComponent.layout(),
    html.Br(),
    html.Button(id = "collapseExpandButton", className = "btn btn-default btn-sm", type = "button", **{"data-toggle": "collapse", "data-target": "#dropdownDiv",
        "aria-expanded": "true", "aria-controls": "dropdownDiv"}, n_clicks = 0, children = ["Collapse"]),
    html.Div(id = "dropdownDiv", className = "collapse in", children =
    [
        html.Div(className = "well well-sm", children =
        [
            dropdowns.enterprisesLayout(),
            dropdowns.sitesLayout(),
            dropdowns.areasLayout(),
            dropdowns.tagsLayout()
        ])
    ]),
    html.Div(children = [dcc.Graph(id = "graph")]),
])
