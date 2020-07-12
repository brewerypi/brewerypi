import re
from flask import current_app, url_for
from jinja2 import Markup
from sqlalchemy import func
from . import customTemplateFilters
from .. models import Element, ElementTemplate, EventFrame, EventFrameTemplate, Site

@customTemplateFilters.app_template_filter()
def message(body):
    pattern = re.compile('^{"EventFrameId":\s"(\d+)",\s"EventFrameTemplateName":\s"(.+)",\s"EventFrameName":\s"(\d+)",\s"EventFrameElement":\s"(.+)"}(.*)$',
        re.DOTALL) # re.DOTALL will even match newlines when using '.'.
    match = pattern.match(body)
    if match:
        eventFrameId = match.group(1)
        eventFrame = EventFrame.query.get(eventFrameId)
        body = match.group(5)
        if eventFrame is not None:
            return Markup('Re: <a href = ' + url_for("eventFrames.dashboard", eventFrameId = eventFrameId) + '>{} Event Frame {} in {}</a><br>{}'. \
                format(eventFrame.EventFrameTemplate.Name, eventFrame.Name, eventFrame.Element.Name, body))
        else:
            eventFrameTemplateName = match.group(2)
            eventFrameName = match.group(3)
            eventFrameElement = match.group(4)
            return Markup('Re: Deleted {} Event Frame {} in {}<br>{}'.format(eventFrameTemplateName, eventFrameName, eventFrameElement, body))
    else:
        return body

@customTemplateFilters.app_template_filter()
def yesNo(boolean):
    if boolean:
        return "Yes"
    else:
        return "No"
