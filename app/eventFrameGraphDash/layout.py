import dash_core_components as dcc
import dash_html_components as html
import dash_table
from app.dashes.helpers import intervalLayout

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
        html.Button(id = "refreshButton", className = "btn btn-default btn-sm", children = [html.Span(className = "glyphicon glyphicon-refresh")]),
        intervalLayout()
    ]),
    html.Br(),
    html.Button(id = "collapseExpandButton", className = "btn btn-default btn-sm", type = "button", **{"data-toggle": "collapse", "data-target": "#dropdownDiv",
        "aria-expanded": "true", "aria-controls": "dropdownDiv"}, n_clicks = 0, children = ["Collapse"]),
    html.Div(id = "dropdownDiv", className = "collapse in", children =
    [
        html.Div(className = "well well-sm", children =
        [
            dcc.Dropdown(id = "enterpriseDropdown", placeholder = "Select Enterprise", multi = False),
            dcc.Dropdown(id = "siteDropdown", placeholder = "Select Site", multi = False),
            dcc.Dropdown(id = "elementTemplateDropdown", placeholder = "Select Element Template", multi = False),
            dcc.Dropdown(id = "eventFrameTemplateDropdown", placeholder = "Select Event Frame Template", multi = False),
            dcc.Dropdown(id = "eventFrameDropdown", placeholder = "Select Event Frame", multi = False),
            dcc.Dropdown(id = "eventFrameTemplateViewDropdown", placeholder = "Select View", multi = False)
        ])
    ]),
    dcc.Graph(id = "graph"),
    html.Div(className = "page-header", children = [html.H2("Notes")]),
    html.Div(className = "well", children =
    [
        dash_table.DataTable(id = "table", sort_action = "native", columns = [{"name": "Timestamp", "id": "Timestamp"}, {"name": "Note", "id": "Note"}],
            style_cell = {"whiteSpace": "normal", "height": "auto", "textAlign": "left"},
            style_cell_conditional = [{"if": {"column_id": "Timestamp"}, "width": "200px"}])
    ])
])
