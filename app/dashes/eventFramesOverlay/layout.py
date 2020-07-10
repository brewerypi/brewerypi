import dash_core_components as dcc
import dash_html_components as html
import dash_table
from app.dashes.components import collapseExpand, elementTemplateDropdown, enterpriseDropdown, eventFrameAttributeTemplatesDropdown, eventFramesDropdown, \
    eventFrameTemplateDropdown, refreshButton, refreshInterval, siteDropdown

layout = html.Div(children =
[
    html.Div(id = "loadingDiv", className = "text-center", children = [html.Img(src = "/static/images/loading.gif")]),
    dcc.Location(id = "url"),
    dcc.Interval(id = "interval", n_intervals = 0, disabled = True),
    html.Div(id = "dashDiv", style = {"display": "none"}, children =
    [
        html.Div(children =
        [
            refreshButton.layout(),
            refreshInterval.layout()
        ]),
        html.Br(),
        collapseExpand.layout(
        [
            enterpriseDropdown.layout(),
            siteDropdown.layout(),
            elementTemplateDropdown.layout(),
            eventFrameTemplateDropdown.layout(),
            eventFramesDropdown.layout(),
        ]),
        eventFrameAttributeTemplatesDropdown.layout(),
        html.Div(children = [dcc.Graph(id = "graph")])
    ])
])
