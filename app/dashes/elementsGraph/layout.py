import dash_core_components as dcc
import dash_html_components as html
from app.dashes.components import collapseExpand, elementsDropdown, elementTemplatesDropdown, enterpriseDropdown, siteDropdown, timeRangePicker

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
            enterpriseDropdown.layout(),
            siteDropdown.layout(),
            elementTemplatesDropdown.layout(),
            elementsDropdown.layout()
        ]),
        html.Div(children = [dcc.Graph(id = "graph")])
    ])
])
