def eventFrameFullyAbbreviatedPath(eventFrame):
	return eventFrame.EventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + \
		eventFrame.EventFrameTemplate.ElementTemplate.Site.Abbreviation + "_" + eventFrame.EventFrameTemplate.ElementTemplate.Name + "_" + eventFrame.EventFrameTemplate.Name + "_" + eventFrame.Name

def eventFrameAttributeTemplateFullyAbbreviatedPath(eventFrameAttributeTemplate):
	return eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Enterprise.Abbreviation + "_" + \
		eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Site.Abbreviation + "_" + \
		eventFrameAttributeTemplate.EventFrameTemplate.ElementTemplate.Name + "_" + \
		eventFrameAttributeTemplate.EventFrameTemplate.Name + "_" + eventFrameAttributeTemplate.Name

def tagFullyAbbreviatedPath(tag):
	return tag.Area.Site.Enterprise.Abbreviation + "_" + tag.Area.Site.Abbreviation + "_" + tag.Area.Abbreviation + "_" + tag.Name
