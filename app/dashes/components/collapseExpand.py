import dash
from dash import html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from urllib.parse import parse_qs, urlparse

def layout(contents):
    return html.Div(id = "collapseExpandDiv", children =
    [
        html.Button(id = "collapseExpandButton", className = "btn btn-default btn-sm", type = "button", **{"data-toggle": "collapse",
            "data-target": "#dropdownDiv", "aria-expanded": "true", "aria-controls": "dropdownDiv"}, n_clicks = 0, children = ["Collapse"]),
        html.Div(id = "dropdownDiv", className = "collapse in", children =
        [
            html.Div(className = "well well-sm", children = contents)
        ])
    ])

def callback(dashApp):
    @dashApp.callback([Output(component_id = "collapseExpandDiv", component_property = "style"),
        Output(component_id = "collapseExpandButton", component_property = "children"),
        Output(component_id = "dropdownDiv", component_property = "className")],
        [Input(component_id = "url", component_property = "href"),
        Input(component_id = "collapseExpandButton", component_property = "n_clicks")],
        [State(component_id = "collapseExpandButton", component_property = "children"),
        State(component_id = "dropdownDiv", component_property = "className")])
    def callback(urlHref, collapseExpandButtonNClicks, collapseExpandButtonChildren, dropdownDivClassName):
        if dash.callback_context.triggered[0]["prop_id"] == ".":
            raise PreventUpdate

        if collapseExpandButtonNClicks == 0:
            queryString = parse_qs(urlparse(urlHref).query)
            if "collapseExpand" in queryString:
                collapseExpand = queryString["collapseExpand"][0]
                if collapseExpand == "collapsed":
                    return {"display": "block"}, ["Expand"], "collapse"
                elif collapseExpand == "expanded":
                    return {"display": "block"}, ["Collapse"], "collapse in"
                elif collapseExpand == "hidden":
                    return {"display": "none"}, ["Collapse"], "collapse in"

            raise PreventUpdate
        else:
            if collapseExpandButtonChildren == ["Collapse"]:
                return {"display": "block"}, ["Expand"], dropdownDivClassName
            else:
                return {"display": "block"}, ["Collapse"], dropdownDivClassName
