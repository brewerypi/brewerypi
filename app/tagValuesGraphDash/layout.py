import dash_core_components as dcc
import dash_html_components as html
from app.dashes import timestampRangeComponent

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
            dcc.Dropdown(id = "enterpriseDropdown", placeholder = "Select Enterprise(s)", multi = True),
            dcc.Dropdown(id = "siteDropdown", placeholder = "Select Site(s)", multi = True),
            dcc.Dropdown(id = "areaDropdown", placeholder = "Select Area(s)", multi = True),
            dcc.Dropdown(id = "tagDropdown", placeholder = "Select Tag(s)", multi = True)
        ])
    ]),
    html.Div(children = [dcc.Graph(id = "graph")]),
])
