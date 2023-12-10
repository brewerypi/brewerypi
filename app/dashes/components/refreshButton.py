from dash import html

def layout():
    return html.Button(id = "refreshButton", className = "btn btn-default btn-sm", children = [html.Span(className = "glyphicon glyphicon-refresh")],
        title = "Refresh")
