from dash.dependencies import Input, Output
from app.models import EventFrame, EventFrameAttribute, LookupValue, TagValue
from app.dashes.components import collapseExpand, elementTemplateDropdown, enterpriseDropdown, eventFrameAttributeTemplatesDropdown, eventFramesDropdown, \
    eventFrameTemplateDropdown, refreshInterval, siteDropdown

def registerCallbacks(dashApp):
    refreshInterval.callback(dashApp)
    collapseExpand.callback(dashApp)
    enterpriseDropdown.optionsCallback(dashApp)
    enterpriseDropdown.valueCallback(dashApp)
    siteDropdown.optionsCallback(dashApp)
    siteDropdown.valueCallback(dashApp)
    elementTemplateDropdown.optionsCallback(dashApp)
    elementTemplateDropdown.valueCallback(dashApp)
    eventFrameTemplateDropdown.optionsCallback(dashApp)
    eventFrameTemplateDropdown.valueCallback(dashApp)
    eventFramesDropdown.optionsCallback(dashApp)
    eventFramesDropdown.valuesCallback(dashApp)
    eventFrameAttributeTemplatesDropdown.optionsCallback(dashApp)
    eventFrameAttributeTemplatesDropdown.valuesCallback(dashApp)

    @dashApp.callback([Output(component_id = "loadingDiv", component_property = "style"),
        Output(component_id = "dashDiv", component_property = "style"),
        Output(component_id = "graph", component_property = "figure")],
        [Input(component_id = "eventFramesDropdown", component_property = "value"),
        Input(component_id = "eventFrameAttributeTemplatesDropdown", component_property = "value"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def graphFigure(eventFramesDropdownValues, eventFrameAttributeTemplatesDropdownValues, intervalNIntervals, refreshButtonNClicks):
        data = []
        if not eventFrameAttributeTemplatesDropdownValues:
            return {"display": "none"}, {"display": "block"}, {"data": data, "layout": {"xaxis": {"title": "Days"}}}

        eventFrames = EventFrame.query.filter(EventFrame.EventFrameId.in_(eventFramesDropdownValues)).order_by(EventFrame.StartTimestamp).all()
        SECONDS_IN_A_DAY = 86400
        for eventFrame in eventFrames:
            eventFrameAttributes = EventFrameAttribute.query.filter(EventFrameAttribute.ElementId == eventFrame.ElementId,
                EventFrameAttribute.EventFrameAttributeTemplateId.in_(eventFrameAttributeTemplatesDropdownValues))
            eventFrameAttributeValues = {}
            for eventFrameAttribute in eventFrameAttributes:
                if eventFrame.EndTimestamp is None:
                    eventFrameAttributeValues[eventFrameAttribute.EventFrameAttributeTemplate.Name] = TagValue.query. \
                        filter(TagValue.TagId == eventFrameAttribute.TagId, TagValue.Timestamp >= eventFrame.StartTimestamp)
                else:
                    eventFrameAttributeValues[eventFrameAttribute.EventFrameAttributeTemplate.Name] = TagValue.query. \
                        filter(TagValue.TagId == eventFrameAttribute.TagId, TagValue.Timestamp >= eventFrame.StartTimestamp,
                            TagValue.Timestamp <= eventFrame.EndTimestamp)

            for eventFrameAttributeTemplateName, tagValues in eventFrameAttributeValues.items():
                seriesName = f"{eventFrame.Name}_{eventFrameAttributeTemplateName}"
                for tagValue in tagValues:
                    # Search for tag dict in list of dicts.
                    listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == seriesName, data))
                    if len(listOfDictionaries) == 0:
                        # Tag dict doesn't exist so append it to the list of dicts.
                        if tagValue.Tag.LookupId is None:
                            data.append(dict(x = [(tagValue.Timestamp - eventFrame.StartTimestamp).total_seconds() / SECONDS_IN_A_DAY],
                                y = [tagValue.Value],
                                text = [tagValue.Tag.UnitOfMeasurement.Abbreviation],
                                name = seriesName,
                                mode = "lines+markers"))
                        else:
                            data.append(dict(x = [(tagValue.Timestamp - eventFrame.StartTimestamp).total_seconds() / SECONDS_IN_A_DAY],
                                y = [tagValue.Value],
                                text = [LookupValue.query.filter_by(LookupId = tagValue.Tag.LookupId, Value = tagValue.Value).one().Name],
                                name = seriesName,
                                mode = "lines+markers"))
                    else:
                        # Tag dict already exists so append to x, y and text.
                        tagDictionary = listOfDictionaries[0]
                        tagDictionary["x"].append((tagValue.Timestamp - eventFrame.StartTimestamp).total_seconds() / SECONDS_IN_A_DAY)
                        tagDictionary["y"].append(tagValue.Value)
                        if tagValue.Tag.LookupId is None:
                            tagDictionary["text"].append(tagValue.Tag.UnitOfMeasurement.Abbreviation)
                        else:
                            tagDictionary["text"].append(LookupValue.query.filter_by(LookupId = tagValue.Tag.LookupId, Value = tagValue.Value).one().Name)

        return {"display": "none"}, {"display": "block"}, {"data": data, "layout": {"uirevision": "no reset", "xaxis": {"title": "Days"}}}
