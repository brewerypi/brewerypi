import dash_core_components as dcc
import dash_html_components as html

layout = html.Div(children =
[
    dcc.Location(id = "url"),
    dcc.Interval(id = "interval", n_intervals = 0, disabled = True),
    html.Div(className = "page-header", children = [html.H1("Event Frame Graph")]),
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
