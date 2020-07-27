import pytz
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from app.models import Element, LookupValue, Note
from app.dashes.components import collapseExpand, elementsDropdown, elementTemplatesDropdown, enterpriseDropdown, siteDropdown, timeRangePicker

def registerCallbacks(dashApp):
    timeRangePicker.callback(dashApp)
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
        Output(component_id = "graph", component_property = "figure")],
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "elementsDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, elementsDropdownValues, urlHref, intervalNIntervals, refreshButtonNClicks):
        if fromTimestampInputValue == "" or toTimestampInputValue == "":
            raise PreventUpdate

        elements = Element.query.filter(Element.ElementId.in_(elementsDropdownValues))
        data = []
        queryString = parse_qs(urlparse(urlHref).query)
        if "localTimezone" in queryString:
            localTimezone = pytz.timezone(queryString["localTimezone"][0])
        else:
            localTimezone = pytz.utc

        fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
        fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
        toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

        for element in elements:
            for elementAttributeTemplateName, tagValues in element.attributeValues(fromTimestampUtc, toTimestampUtc).items():
                seriesName = "{}_{}".format(element.Name, elementAttributeTemplateName)
                for tagValue in tagValues:
                    # Search for tag dict in list of dicts.
                    listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == seriesName, data))
                    if len(listOfDictionaries) == 0:
                        # Tag dict doesn't exist so append it to the list of dicts.
                        if tagValue.Tag.LookupId is None:
                            data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                                y = [tagValue.Value],
                                text = [tagValue.Tag.UnitOfMeasurement.Abbreviation],
                                name = seriesName,
                                mode = "lines+markers"))
                        else:
                            data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                                y = [tagValue.Value],
                                text = [LookupValue.query.filter_by(LookupId = tagValue.Tag.LookupId, Value = tagValue.Value).one().Name],
                                name = seriesName,
                                mode = "lines+markers"))
                    else:
                        # Tag dict already exists so append to x, y and text.
                        tagDictionary = listOfDictionaries[0]
                        tagDictionary["x"].append(pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone))
                        tagDictionary["y"].append(tagValue.Value)
                        if tagValue.Tag.LookupId is None:
                            tagDictionary["text"].append(tagValue.Tag.UnitOfMeasurement.Abbreviation)
                        else:
                            tagDictionary["text"].append(LookupValue.query.filter_by(LookupId = tagValue.Tag.LookupId, Value = tagValue.Value).one().Name)

                    if tagValue.TagValueNotes.count() > 0:
                        tagValueNotes = ""
                        for n, tagValueNote in enumerate(tagValue.TagValueNotes, start = 1):
                            note = "{}: {}".format(pytz.utc.localize(tagValueNote.Note.Timestamp).astimezone(localTimezone), tagValueNote.Note.Note)
                            if n != 1:
                                note = "<br>" + note
                            
                            tagValueNotes = tagValueNotes + note

                        # Search for tag notes dict in list of dicts.
                        listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == "{} Notes".format(seriesName), data))
                        if len(listOfDictionaries) == 0:
                            # Tag notes dict doesn't exist so append it to the list of dicts.
                            data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                                y = [tagValue.Value],
                                text = [tagValueNotes],
                                name = "{} Notes".format(seriesName),
                                mode = "markers"))
                        else:
                            # Tag notes dict already exists so append to x, y and text.
                            tagNotesDictionary = listOfDictionaries[0]
                            tagNotesDictionary["x"].append(pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone))
                            tagNotesDictionary["y"].append(tagValue.Value)
                            tagNotesDictionary["text"].append(tagValueNotes)
                
        return {"display": "none"}, {"display": "block"}, {"data": data, "layout": {"uirevision": "no reset"}}
