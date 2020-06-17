import dash_core_components as dcc
import dash_html_components as html
from app.dashes.components import collapseExpandButton, elementsDropdown, elementTemplatesDropdown, enterpriseDropdown, refreshButton, refreshInterval, \
     siteDropdown

layout = html.Div(children =
[
    dcc.Location(id = "url"),
    dcc.Interval(id = "interval", n_intervals = 0, disabled = True),
    html.Div(className = "page-header", children = [html.H1("Element Summary")]),
    html.Div(children = [
        refreshButton.layout(),
        refreshInterval.layout()
    ]),
    html.Br(),
    collapseExpandButton.layout("dropdownDiv"),
    html.Div(id = "dropdownDiv", className = "collapse in", children =
    [
        html.Div(className = "well well-sm", children =
        [
            enterpriseDropdown.layout(),
            siteDropdown.layout(),
            elementTemplatesDropdown.layout(),
            elementsDropdown.layout()
        ])
    ])
])
