""" lens caching """
from zope import interface, component
from zope.component import getGlobalSiteManager
from zope.app.event.interfaces import IObjectModifiedEvent
from zope.app.container.interfaces import IObjectAddedEvent
from zope.app.container.interfaces import IObjectRemovedEvent
from Products.CMFCore.utils import getToolByName
from Products.Lensmaker.SelectedContent import SelectedContent
from Products.Lensmaker.ContentSelectionLens import ContentSelectionLens
from Products.RhaptosCollection.interfaces import ICollection

sm = component.getGlobalSiteManager()

types = {'List': 'memberlists',
	 'Endorsement': 'endorsements',
	 'Affiliation': 'affiliations'}

def purgeContent(ob, stool):
    content = getToolByName(ob, 'content')

    try:
	content = content.getRhaptosObject(ob.getId(), 'latest').getTarget()
    except:
        return

    paths = ['content/%s/'%content.aq_parent.getId()]

    if ICollection.providedBy(content):
	paths.extend(['content/%s/'%m for m in content.containedModuleIds()])

    print content, paths

    stool.pruneUrls(paths, 'PURGE_REGEXP')


def objectAddedEvent(ob, ev):
    stool = getToolByName(ob, 'portal_squid', None)
    if stool is None:
	return
    
    lens = ev.newParent

    state = lens.review_state()
    lid = lens.getId()
    uid = lens.aq_parent.getId()

    stool.pruneUrls(['lenses/%s/%s'%(uid, lid)], 'PURGE_REGEXP')

    paths = ['lenses/%s/'%uid]

    # purge additional urls for public lenses
    if state == 'published':
	paths.append('lenses')

	tp = types.get(lens.category, None)
	if tp is not None:
	    paths.append(tp)

    stool.pruneUrls(paths)
    purgeContent(ob, stool)

getGlobalSiteManager().subscribe((SelectedContent, IObjectAddedEvent,), None, objectAddedEvent)


def objectRemovedEvent(ob, ev):
    stool = getToolByName(ob, 'portal_squid', None)
    if stool is None:
	return

    #deleting from lens, or the whole lens?
    if ob == ev.object:
        lens = ev.oldParent
    else:
        lens = ev.object

    state = lens.review_state()
    lid = lens.getId()
    uid = lens.aq_parent.getId()

    stool.pruneUrls(['lenses/%s/%s'%(uid, lid)], 'PURGE_REGEXP')

    paths = ['lenses/%s/'%uid]

    # purge additional urls for public lenses
    if state == 'published':
	paths.append('/lenses')

	tp = types.get(lens.category, None)
	if tp is not None:
	    paths.append(tp)

    stool.pruneUrls(paths)
    purgeContent(ob, stool)

getGlobalSiteManager().subscribe((SelectedContent, IObjectRemovedEvent,), None, objectRemovedEvent)


def objectModifiedEvent(lens, ev):
    stool = getToolByName(lens, 'portal_squid', None)
    if stool is None:
	return

    state = lens.review_state()
    lid = lens.getId()
    uid = lens.aq_parent.getId()

    stool.pruneUrls(['lenses/%s/%s'%(uid, lid)], 'PURGE_REGEXP')

    paths = ['lenses/%s/'%uid]

    # purge additional urls for public lenses
    if state == 'published':
	paths.append('/lenses')

	tp = types.get(lens.category, None)
	if tp is not None:
	    paths.append(tp)

    stool.pruneUrls(paths)


getGlobalSiteManager().subscribe((ContentSelectionLens, IObjectModifiedEvent,), None, objectModifiedEvent)
