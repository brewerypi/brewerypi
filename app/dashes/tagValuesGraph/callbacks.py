import pytz
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from datetime import datetime
from urllib.parse import parse_qs, urlparse
from app.models import LookupValue, Tag, TagValue
from app.dashes.components import areasDropdown, collapseExpand, enterprisesDropdown, sitesDropdown, tagsDropdown, timeRangePicker

def registerCallbacks(dashApp):
    timeRangePicker.callback(dashApp)
    collapseExpand.callback(dashApp)
    enterprisesDropdown.optionsCallback(dashApp)
    enterprisesDropdown.valuesCallback(dashApp)
    sitesDropdown.optionsCallback(dashApp)
    sitesDropdown.valuesCallback(dashApp)
    areasDropdown.optionsCallback(dashApp)
    areasDropdown.valuesCallback(dashApp)
    tagsDropdown.optionsCallback(dashApp)
    tagsDropdown.valuesCallback(dashApp)

    @dashApp.callback([Output(component_id = "loadingDiv", component_property = "style"),
        Output(component_id = "dashDiv", component_property = "style"),
        Output(component_id = "graph", component_property = "figure")],
        [Input(component_id = "fromTimestampInput", component_property = "value"),
        Input(component_id = "toTimestampInput", component_property = "value"),
        Input(component_id = "tagsDropdown", component_property = "value"),
        Input(component_id = "url", component_property = "href"),
        Input(component_id = "interval", component_property = "n_intervals"),
        Input(component_id = "refreshButton", component_property = "n_clicks")])
    def graphFigure(fromTimestampInputValue, toTimestampInputValue, tagsDropdownValues, urlHref, intervalNIntervals, refreshButtonNClicks):
        if fromTimestampInputValue is None or toTimestampInputValue is None or tagsDropdownValues is None:
            raise PreventUpdate
        else:
            data = []
            if fromTimestampInputValue!= "" and toTimestampInputValue != "" and tagsDropdownValues is not None:
                queryString = parse_qs(urlparse(urlHref).query)
                if "localTimezone" in queryString:
                    localTimezone = pytz.timezone(queryString["localTimezone"][0])
                else:
                    localTimezone = pytz.utc

                fromTimestampLocal = localTimezone.localize(datetime.strptime(fromTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                toTimestampLocal = localTimezone.localize(datetime.strptime(toTimestampInputValue, "%Y-%m-%dT%H:%M:%S"))
                fromTimestampUtc = fromTimestampLocal.astimezone(pytz.utc)
                toTimestampUtc = toTimestampLocal.astimezone(pytz.utc)

                for tagId in tagsDropdownValues:
                    tag = Tag.query.get(tagId)
                    tagValues = TagValue.query.filter(TagValue.TagId == tag.TagId, TagValue.Timestamp >= fromTimestampUtc, TagValue.Timestamp <= toTimestampUtc)
                    if tag.LookupId is None:
                        data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone) for tagValue in tagValues],
                            y = [tagValue.Value for tagValue in tagValues],
                            text = [tagValue.Tag.UnitOfMeasurement.Abbreviation for tagValue in tagValues],
                            name = tag.Name,
                            mode = "lines+markers"))
                    else:
                        data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone) for tagValue in tagValues],
                            y = [tagValue.Value for tagValue in tagValues],
                            text = [LookupValue.query.filter_by(LookupId = tag.LookupId, Value = tagValue.Value).one().Name for tagValue in tagValues],
                            name = tag.Name,
                            mode = "lines+markers"))

                    for tagValue in tagValues:
                        if tagValue.TagValueNotes.count() > 0:
                            tagValueNotes = ""
                            for n, tagValueNote in enumerate(tagValue.TagValueNotes, start = 1):
                                note = "{}: {}".format(pytz.utc.localize(tagValueNote.Note.Timestamp).astimezone(localTimezone), tagValueNote.Note.Note)
                                if n != 1:
                                    note = "<br>" + note
                                
                                tagValueNotes = tagValueNotes + note

                            # Search for tag notes dict in list of dicts.
                            listOfDictionaries = list(filter(lambda dictionary: dictionary["name"] == "{} Notes".format(tagValue.Tag.Name), data))
                            if len(listOfDictionaries) == 0:
                                # Tag notes dict doesn't exist so append it to the list of dicts.
                                data.append(dict(x = [pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone)],
                                    y = [tagValue.Value],
                                    text = [tagValueNotes],
                                    name = "{} Notes".format(tagValue.Tag.Name),
                                    mode = "markers"))
                            else:
                                # Tag notes dict already exists so append to x, y and text.
                                tagNotesDictionary = listOfDictionaries[0]
                                tagNotesDictionary["x"].append(pytz.utc.localize(tagValue.Timestamp).astimezone(localTimezone))
                                tagNotesDictionary["y"].append(tagValue.Value)
                                tagNotesDictionary["text"].append(tagValueNotes)

            return {"display": "none"}, {"display": "block"}, {"data": data, "layout": {"uirevision": "no reset"}}
