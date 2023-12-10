from dash import dcc
from dash import html
from dash import dash_table
from app.dashes.components import collapseExpand, elementTemplateDropdown, enterpriseDropdown, eventFrameDropdown, eventFrameTemplateDropdown, \
    eventFrameTemplateViewDropdown, siteDropdown, timeRangePicker

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
            eventFrameDropdown.layout(),
        ]),
        eventFrameTemplateViewDropdown.layout(),
        html.Div(children = [dcc.Graph(id = "graph")]),
        html.Div(className = "page-header", children = [html.H2("Notes")]),
        html.Div(className = "well", children =
        [
            dash_table.DataTable(id = "table", cell_selectable = False, sort_action = "native", columns = [{"name": "Timestamp", "id": "Timestamp"},
                {"name": "Note", "id": "Note"}], style_cell = {"whiteSpace": "normal", "height": "auto", "textAlign": "left"},
                style_cell_conditional = [{"if": {"column_id": "Timestamp"}, "width": "200px"}])
        ])
    ])
])
