import dash_core_components as dcc
import dash_html_components as html

layout = html.Div \
(
    children =
    [
        dcc.Location(id = "url"),
        dcc.Dropdown(id = "eventFrameDropdown", placeholder = "Select Event Frame", multi = False),
        dcc.Dropdown(id = "eventFrameTemplateViewDropdown", placeholder = "Select View", multi = False),
        dcc.Graph(id = "graph")
    ]
)
