import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
from urllib.parse import parse_qs, urlparse
from app.models import Area, Enterprise, Site, Tag

def layout():
    return dcc.Dropdown(id = "tagsDropdown", placeholder = "Select Tag(s)", multi = True)

def optionsCallback(dashApp):
    @dashApp.callback(Output(component_id = "tagsDropdown", component_property = "options"),
        [Input(component_id = "areasDropdown", component_property = "value")])
    def tagsDropdownOptions(areasDropdownValues):
        return [{"label": "{}_{}_{}_{}".format(tag.Area.Site.Enterprise.Abbreviation, tag.Area.Site.Abbreviation, tag.Area.Abbreviation, tag.Name),
            "value": tag.TagId} for tag in Tag.query.join(Area, Site, Enterprise).filter(Tag.AreaId.in_(areasDropdownValues)).\
            order_by(Enterprise.Abbreviation, Site.Abbreviation, Area.Abbreviation, Tag.Name).all()]

def valuesCallback(dashApp):
    @dashApp.callback(Output(component_id = "tagsDropdown", component_property = "value"),
        [Input(component_id = "tagsDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")],
        [State(component_id = "tagsDropdown", component_property = "value")])
    def tagsDropdownValues(tagsDropdownOptions, urlHref, tagsDropdownValues):
        tagIds = []
        if len(list(filter(lambda property: property["prop_id"] == "url.href", dash.callback_context.triggered))) > 0:
            if tagsDropdownOptions:
                queryString = parse_qs(urlparse(urlHref).query)
                if "tagId" in queryString:
                    for tagId in map(int, queryString["tagId"]):
                        if len(list(filter(lambda tag: tag["value"] == tagId, tagsDropdownOptions))) > 0:
                            tagIds.append(tagId)
        else:
            if tagsDropdownOptions and tagsDropdownValues:
                for tagId in tagsDropdownValues:
                    if len(list(filter(lambda tag: tag["value"] == tagId, tagsDropdownOptions))) > 0:
                        tagIds.append(tagId)

        return tagIds
