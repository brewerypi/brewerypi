from sqlalchemy import func
from . import customTemplateFilters
from .. models import Element, ElementTemplate, EventFrame, Site

@customTemplateFilters.app_template_filter()
def grafanaUrl(uid, parameters):
    if uid == "ElementSummary":
        if "siteId" in parameters:
            site = Site.query.get_or_404(parameters["siteId"])
            return "http://localhost:3000/d/ElementSummary/element-summary?orgId=1" + \
                "&var-enterprise={}".format(site.Enterprise.EnterpriseId) + \
                "&var-site={}".format(parameters["siteId"]) + \
                "&var-elementTemplates=All" + \
                "&var-elements=All" + \
                "&var-attributeTemplates=All"
        elif "elementTemplateId" in parameters:
            elementTemplate = ElementTemplate.query.get_or_404(parameters["elementTemplateId"])
            elements = ""
            for element in elementTemplate.Elements:
                elements += "&var-elements={}".format(element.ElementId)
            return "http://localhost:3000/d/ElementSummary/element-summary?orgId=1" + \
                "&var-enterprise={}".format(elementTemplate.Site.Enterprise.EnterpriseId) + \
                "&var-site={}".format(elementTemplate.Site.SiteId) + \
                "&var-elementTemplates={}".format(elementTemplate.ElementTemplateId) + \
                elements + \
                "&var-attributeTemplates=All"
    elif uid == "ElementValuesGraph":
        element = Element.query.get_or_404(parameters["elementId"])
        return "http://localhost:3000/d/ElementValuesGraph/element-values-graph?orgId=1" + \
            "&var-enterprise={}".format(element.ElementTemplate.Site.Enterprise.EnterpriseId) + \
            "&var-site={}".format(element.ElementTemplate.Site.SiteId) + \
            "&var-elementTemplates=All" + \
            "&var-elements={}".format(parameters["elementId"]) + \
            "&var-attributeTemplates=All" + \
            "&var-lookups=All"
    elif uid == "EventFramesGraph":
        eventFrame = EventFrame.query.get_or_404(parameters["eventFrameId"])
        startTimestamp = EventFrame.query.with_entities(func.unix_timestamp(EventFrame.StartTimestamp)).filter_by(EventFrameId = eventFrame.EventFrameId). \
            one()[0]
        if eventFrame.EndTimestamp:
            endTimestamp = EventFrame.query.with_entities(func.unix_timestamp(EventFrame.EndTimestamp)).filter_by(EventFrameId = eventFrame.EventFrameId). \
                one()[0]
            return "http://localhost:3000/d/EventFramesGraph/event-frames-graph?orgId=1" + \
                "&from={}000".format(startTimestamp) + \
                "&to={}000".format(endTimestamp) + \
                "&var-enterprise={}".format(eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId) + \
                "&var-site={}".format(eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId) + \
                "&var-elementTemplate={}".format(eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId) + \
                "&var-eventFrameTemplate={}".format(eventFrame.EventFrameTemplate.EventFrameTemplateId) + \
                "&var-eventFrame={}".format(parameters["eventFrameId"]) + \
                "&var-attributeTemplates=All" + \
                "&var-lookups=All"
        else:
            return "http://localhost:3000/d/EventFramesGraph/event-frames-graph?orgId=1" + \
                "&from={}000".format(startTimestamp) + \
                "&to=now" + \
                "&var-enterprise={}".format(eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.EnterpriseId) + \
                "&var-site={}".format(eventFrame.EventFrameTemplate.ElementTemplate.Site.SiteId) + \
                "&var-elementTemplate={}".format(eventFrame.EventFrameTemplate.ElementTemplate.ElementTemplateId) + \
                "&var-eventFrameTemplate={}".format(eventFrame.EventFrameTemplate.EventFrameTemplateId) + \
                "&var-eventFrame={}".format(parameters["eventFrameId"]) + \
                "&var-attributeTemplates=All" + \
                "&var-lookups=All"
    elif uid == "TagValuesGraph":
        return "http://localhost:3000/d/TagValuesGraph/tag-values-graph?orgId=1" + \
            "&var-enterprises=All" + \
            "&var-sites=All" + \
            "&var-areas=All" + \
            "&var-tags={}".format(parameters["tagId"]) + \
            "&var-lookups=All"
