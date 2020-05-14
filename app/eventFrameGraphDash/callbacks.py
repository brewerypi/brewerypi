from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from urllib.parse import parse_qs, urlparse
from app.models import ElementTemplate, Enterprise, EventFrame, EventFrameTemplate, EventFrameTemplateView, Site

def registerCallbacks(dashApp):
    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def enterpriseDropDownOptions(urlHref):
        return [{"label": enterprise.Name, "value": enterprise.EnterpriseId} for enterprise in Enterprise.query.order_by(Enterprise.Name).all()]

    @dashApp.callback(Output(component_id = "enterpriseDropdown", component_property = "value"),
        [Input(component_id = "enterpriseDropdown", component_property = "options"),
        Input(component_id = "url", component_property = "href")])
    def enterpriseDropdownValue(enterpriseDropdownOptions, urlHref):
        if enterpriseDropdownOptions is None:
            raise PreventUpdate
        else:
            queryString = parse_qs(urlparse(urlHref).query)
            if "enterpriseId" in queryString:
                return int(queryString["enterpriseId"][0])
            else:
                return enterpriseDropdownOptions[0]["value"]

    @dashApp.callback([Output(component_id = "siteDropdown", component_property = "options"),
        Output(component_id = "siteDropdown", component_property = "value")],
        [Input(component_id = "enterpriseDropdown", component_property = "value")])
    def siteDropdownOptions(enterpriseDropdownValue):
        return [[{"label": site.Name, "value": site.SiteId} for site in Site.query.filter_by(EnterpriseId = enterpriseDropdownValue). \
            order_by(Site.Name).all()], None]

    @dashApp.callback([Output(component_id = "elementTemplateDropdown", component_property = "options"),
        Output(component_id = "elementTemplateDropdown", component_property = "value")],
        [Input(component_id = "siteDropdown", component_property = "value")])
    def elementTemplateDropdownOptions(siteDropdownValue):
        return [[{"label": elementTemplate.Name, "value": elementTemplate.ElementTemplateId} for elementTemplate in ElementTemplate.query. \
            filter_by(SiteId = siteDropdownValue).order_by(ElementTemplate.Name).all()], None]

    @dashApp.callback([Output(component_id = "eventFrameTemplateDropdown", component_property = "options"),
        Output(component_id = "eventFrameTemplateDropdown", component_property = "value")],
        [Input(component_id = "elementTemplateDropdown", component_property = "value")])
    def eventFrameTemplateDropdownOptions(elementTemplateDropdownValue):
        return [[{"label": eventFrameTemplate.Name, "value": eventFrameTemplate.EventFrameTemplateId} for eventFrameTemplate in EventFrameTemplate.query. \
            filter_by(ElementTemplateId = elementTemplateDropdownValue).order_by(EventFrameTemplate.Name).all()], None]

    @dashApp.callback([Output(component_id = "eventFrameDropdown", component_property = "options"),
        Output(component_id = "eventFrameDropdown", component_property = "value")],
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameDropdownOptions(eventFrameTemplateDropdownValue):
        return [[{"label": eventFrame.Name, "value": eventFrame.EventFrameId} for eventFrame in EventFrame.query. \
            filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue).order_by(EventFrame.StartTimestamp.desc()).all()], None]

    @dashApp.callback([Output(component_id = "eventFrameTemplateViewDropdown", component_property = "options"),
        Output(component_id = "eventFrameTemplateViewDropdown", component_property = "value")],
        [Input(component_id = "eventFrameTemplateDropdown", component_property = "value")])
    def eventFrameDropdownOptions(eventFrameTemplateDropdownValue):
        if eventFrameTemplateDropdownValue is None:
            return [[], None]

        eventFrameTemplateViews = [{"label": eventFrameTemplateView.Name, "value": eventFrameTemplateView.EventFrameTemplateViewId}
            for eventFrameTemplateView in EventFrameTemplateView.query.filter_by(EventFrameTemplateId = eventFrameTemplateDropdownValue). \
                order_by(EventFrameTemplateView.Name).all()]
        eventFrameTemplateViews.insert(0, {"label": "All", "value": -1})
        return [eventFrameTemplateViews, -1]

    @dashApp.callback(Output(component_id = "graph", component_property = "figure"),
        [Input(component_id = "eventFrameDropdown", component_property = "value"),
        Input(component_id = "eventFrameTemplateViewDropdown", component_property = "value")])
    def graphFigure(eventFrameDropdownValue, eventFrameTemplateViewDropdownValue):
        if eventFrameDropdownValue is None:
            raise PreventUpdate

        eventFrame = EventFrame.query.get(eventFrameDropdownValue)
        data = []
        for tagValue in eventFrame.attributeValues(eventFrameTemplateViewDropdownValue):
            # Search for tag name dict in list of dicts.
            tags = list(filter(lambda tag: tag["name"] == tagValue.Tag.Name, data))
            if len(tags) == 0:
                # Tag name dict doesn't exist so append it to the list of dicts.
                data.append(dict(x = [tagValue.Timestamp],
                    y = [tagValue.Value],
                    name = tagValue.Tag.Name,
                    mode = "lines+markers"))
            else:
                # Tag name dict already exists so append to x and y.
                seriesDict = tags[0]
                seriesDict["x"].append(tagValue.Timestamp)
                seriesDict["y"].append(tagValue.Value)

        return {"data": data}
