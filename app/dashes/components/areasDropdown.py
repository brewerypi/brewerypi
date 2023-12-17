from dash import dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import Area, Enterprise, Site

def layout():
    return dcc.Dropdown(id = "areasDropdown", placeholder = "Select Area(s)", multi = True, value = -1)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "areasDropdown", component_property = "options"),
        [Input(component_id = "sitesDropdown", component_property = "value")])
    def areasDropdownOptions(sitesDropdownValues):
        return [{"label": "{}_{}_{}".format(area.Site.Enterprise.Abbreviation, area.Site.Abbreviation, area.Name), "value": area.AreaId} for area in 
            Area.query.join(Site).join(Enterprise).filter(Area.SiteId.in_(sitesDropdownValues)).order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "areasDropdown", component_property = "value"),
        [Input(component_id = "areasDropdown", component_property = "options")],
        [State(component_id = "url", component_property = "href"),
        State(component_id = "areasDropdown", component_property = "value")])
    def areasDropdownValues(areasDropdownOptions, urlHref, areasDropdownValues):
        areaIds = []
        if areasDropdownValues == -1:
            if areasDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "areaId" in queryString:
                    for areaId in map(int, queryString["areaId"]):
                        if len(list(filter(lambda area: area["value"] == areaId, areasDropdownOptions))) > 0:
                            areaIds.append(areaId)
        else:
            if areasDropdownOptions and areasDropdownValues:
                for areaId in areasDropdownValues:
                    if len(list(filter(lambda area: area["value"] == areaId, areasDropdownOptions))) > 0:
                        areaIds.append(areaId)

        return areaIds
