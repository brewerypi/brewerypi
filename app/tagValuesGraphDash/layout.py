import dash_core_components as dcc
import dash_html_components as html

layout = html.Div(children = [dcc.Location(id = "url"),
    html.Div(children = [dcc.Dropdown(id = "enterprisesDropdown", placeholder = "Select Enterprise(s)", multi = True),
        dcc.Dropdown(id = "sitesDropdown", placeholder = "Select Site(s)", multi = True),
        dcc.Dropdown(id = "areasDropdown", placeholder = "Select Area(s)", multi = True),
        dcc.Dropdown(id = "tagsDropdown", placeholder = "Select Tag(s)", multi = True)]),
    html.Br(),
    html.Div(children = [html.Label("From: "),
        dcc.Input(id = "fromTimestampInput", type = "datetime-local"),
        html.Label(" to: "),
        dcc.Input(id = "toTimestampInput", type = "datetime-local")]),
    dcc.Graph(id = "graph")])
