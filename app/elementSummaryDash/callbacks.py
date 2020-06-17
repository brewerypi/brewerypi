from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from app.dashes.components import collapseExpandButton, elementsDropdown, elementTemplatesDropdown, enterpriseDropdown, refreshInterval, siteDropdown

def registerCallbacks(dashApp):
    refreshInterval.callback(dashApp)
    collapseExpandButton.callback(dashApp)
    enterpriseDropdown.optionsCallback(dashApp)
    enterpriseDropdown.valueCallback(dashApp)
    siteDropdown.optionsCallback(dashApp)
    siteDropdown.valueCallback(dashApp)
    elementTemplatesDropdown.optionsCallback(dashApp)
    elementTemplatesDropdown.valuesCallback(dashApp)
    elementsDropdown.optionsCallback(dashApp)
    elementsDropdown.valuesCallback(dashApp)
