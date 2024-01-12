from dash import dcc
from dash import html
from app.dashes.components import collapseExpand, elementTemplateDropdown, enterpriseDropdown, eventFrameAttributeTemplateDropdown, \
    eventFrameTemplateDropdown, siteDropdown, timeRangePicker

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
            elementTemplateDropdown.layout(),
            eventFrameTemplateDropdown.layout(),
        ]),
        html.Div(children = [dcc.Dropdown(id = "subgroupLookupDropdown", placeholder = "Select Subgroup Lookup", multi = False, value = -1)]),
        html.Div(children = [dcc.Dropdown(id = "subgroupLookupValueDropdown", placeholder = "Select Subgroup Value", multi = False, value = -1)]),
        eventFrameAttributeTemplateDropdown.layout(),
        html.Div(className = "page-header", children = [html.H2("Individual")]),
        html.Div(children = [dcc.Graph(id = "individualGraph")]),
        html.Div(className = "page-header", children = [html.H2("Moving Range")]),
        html.Div(children = [dcc.Graph(id = "movingRangeGraph")])
    ])
])
