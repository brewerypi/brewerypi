import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

def layout(collapsableDivIdName):
    return html.Button(id = "collapseExpandButton", className = "btn btn-default btn-sm", type = "button", **{"data-toggle": "collapse",
        "data-target": "#{}".format(collapsableDivIdName), "aria-expanded": "true", "aria-controls": collapsableDivIdName}, n_clicks = 0, children = ["Collapse"])

def callback(dashApp):
    @dashApp.callback(Output(component_id = "collapseExpandButton", component_property = "children"),
        [Input(component_id = "collapseExpandButton", component_property = "n_clicks")],
        [State(component_id = "collapseExpandButton", component_property = "children")])
    def callback(collapseExpandButtonNClicks, collapseExpandButtonChildren):
        if collapseExpandButtonNClicks == 0:
            raise PreventUpdate
        else:
            if collapseExpandButtonChildren == ["Collapse"]:
                return ["Expand"]
            else:
                return ["Collapse"]
