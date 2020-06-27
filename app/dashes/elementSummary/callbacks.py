import pandas as pd
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from app import db
from app.dashes.components import collapseExpand, elementsDropdown, elementTemplatesDropdown, enterpriseDropdown, refreshInterval, siteDropdown
from .sql import elementAttributeValues

def registerCallbacks(dashApp):
    refreshInterval.callback(dashApp)
    collapseExpand.callback(dashApp)
    enterpriseDropdown.optionsCallback(dashApp)
    enterpriseDropdown.valueCallback(dashApp)
    siteDropdown.optionsCallback(dashApp)
    siteDropdown.valueCallback(dashApp)
    elementTemplatesDropdown.optionsCallback(dashApp)
    elementTemplatesDropdown.valuesCallback(dashApp)
    elementsDropdown.optionsCallback(dashApp)
    elementsDropdown.valuesCallback(dashApp)

    @dashApp.callback([Output(component_id = "loadingDiv", component_property = "style"),
        Output(component_id = "dashDiv", component_property = "style"),
        Output(component_id = "table", component_property = "columns"),
        Output(component_id = "table", component_property = "data")],
        [Input(component_id = "elementsDropdown", component_property = "value"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def elementsDropdownValue(elementsDropdownValues, intervalNIntervals, refreshButtonNClicks):
        if len(elementsDropdownValues) == 0:
            elementIds = [-1]
        else:
            elementIds = elementsDropdownValues

        df = pd.read_sql(elementAttributeValues(elementIds), db.session.bind)
        return {"display": "none"}, {"display": "block"}, [{"name": column, "id": column, "hideable": True} for column in df.columns], df.to_dict("records")
