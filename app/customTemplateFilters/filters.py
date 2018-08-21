from sqlalchemy import func
from . import customTemplateFilters
from .. models import EventFrame

@customTemplateFilters.app_template_filter()
def grafanaUrl(uid, id):
    if uid == "ElementValuesGraph":
        return "http://localhost:3000/d/ElementValuesGraph/element-values-graph?orgId=1&var-enterprise=2&var-site=2&var-elementTemplates=All" + \
            "&var-elements={}&var-attributeTemplates=All&var-lookups=All".format(id)
    elif uid == "EventFramesGraph":
        eventFrame = EventFrame.query.get_or_404(id)
        startTimestamp = EventFrame.query.with_entities(func.unix_timestamp(EventFrame.StartTimestamp)).filter_by(EventFrameId = eventFrame.EventFrameId). \
            one()[0]
        if eventFrame.EndTimestamp:
            endTimestamp = EventFrame.query.with_entities(func.unix_timestamp(EventFrame.EndTimestamp)).filter_by(EventFrameId = eventFrame.EventFrameId). \
                one()[0]
            return "http://localhost:3000/d/EventFramesGraph/event-frames-graph?orgId=1&from={}000".format(startTimestamp) + \
                "&to={}000".format(endTimestamp) + \
                "&var-enterprise=2&var-site=2&var-elementTemplate=4&var-eventFrameTemplate=1&var-eventFrame={}".format(eventFrame.EventFrameId) + \
                "&var-attributeTemplates=All&var-lookups=All"
        else:
            return "http://localhost:3000/d/EventFramesGraph/event-frames-graph?orgId=1&from={}000".format(startTimestamp) + \
                "&to=now&var-enterprise=2&var-site=2&var-elementTemplate=4&var-eventFrameTemplate=1&var-eventFrame={}".format(eventFrame.EventFrameId) + \
                "&var-attributeTemplates=All&var-lookups=All"
    elif uid == "TagValuesGraph":
        return "http://localhost:3000/d/TagValuesGraph/tag-values-graph?orgId=1&var-enterprises=All&var-sites=All&var-areas=All&var-tags={}&var-lookups=All". \
            format(id)
