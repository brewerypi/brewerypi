from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from app.models import EventFrame, EventFrameTemplateView

def registerCallbacks(dashApp):
    @dashApp.callback(Output(component_id = "eventFrameDropdown", component_property = "options"),
        [Input(component_id = "url", component_property = "href")])
    def eventFrameDropdown(urlHref):
        return [{"label": eventFrame.Name, "value": eventFrame.EventFrameId} for eventFrame in
            EventFrame.query.order_by(EventFrame.StartTimestamp.desc()).all()]

    @dashApp.callback([Output(component_id = "graph", component_property = "figure"),
        Output(component_id = "eventFrameTemplateViewDropdown", component_property = "options")],
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

        eventFrameTemplateViews = [{"label": eventFrameTemplateView.Name, "value": eventFrameTemplateView.EventFrameTemplateViewId}
            for eventFrameTemplateView in EventFrameTemplateView.query.filter_by(EventFrameTemplateId = eventFrame.EventFrameTemplateId). \
                order_by(EventFrameTemplateView.Name).all()]
        eventFrameTemplateViews.insert(0, {"label": "All", "value": -1})
        return [{"data": data}, eventFrameTemplateViews]
