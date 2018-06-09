def areaFullyAbbreviatedPath(area):
	return area.Site.Enterprise.Abbreviation + "_" + area.Site.Abbreviation + "_" + area.Abbreviation

def elementAttributeTemplateFullyAbbreviatedPath(elementAttributeTemplate):
	return elementAttributeTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + elementAttributeTemplate.ElementTemplate.Site.Abbreviation + "_" + elementAttributeTemplate.ElementTemplate.Name + "_" + elementAttributeTemplate.Name

def elementFullyAbbreviatedPath(element):
	return element.ElementTemplate.Site.Enterprise.Abbreviation + "_" + element.ElementTemplate.Site.Abbreviation + "_" + element.ElementTemplate.Name + "_" + element.Name

def elementTemplateFullyAbbreviatedPath(elementTemplate):
	return elementTemplate.Site.Enterprise.Abbreviation + "_" + elementTemplate.Site.Abbreviation + "_" + elementTemplate.Name

def eventFrameFullyAbbreviatedPath(eventFrame):
	return eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + eventFrame.EventFrameTemplate.ElementTemplate.Site.Abbreviation + "_" + eventFrame.EventFrameTemplate.ElementTemplate.Name + "_" + eventFrame.EventFrameTemplate.Name + "_" + eventFrame.Name

def eventFrameAttributeTemplateFullyAbbreviatedPath(eventFrameAttributeTemplate):
	return eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Abbreviation + "_" + eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Name + "_" + eventFrameAttributeTemplate.EventFrameTemplate.Name + "_" + eventFrameAttributeTemplate.Name

def eventFrameTemplateFullyAbbreviatedPath(eventFrameTemplate):
	return eventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + eventFrameTemplate.ElementTemplate.Site.Abbreviation + "_" + eventFrameTemplate.ElementTemplate.Name + "_" + eventFrameTemplate.Name

def siteFullyAbbreviatedPath(site):
	return site.Enterprise.Abbreviation + "_" + site.Abbreviation

def tagFullyAbbreviatedPath(tag):
	return tag.Area.Site.Enterprise.Abbreviation + "_" + tag.Area.Site.Abbreviation + "_" + tag.Area.Abbreviation + "_" + tag.Name
