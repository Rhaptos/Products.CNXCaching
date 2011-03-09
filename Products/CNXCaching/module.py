""" hook into module revision publishing """
#FIXME: this needs to be changed if we ever properly implement new Collection Version spec

from Products.CMFSquidTool import queue
from Products.CMFCore.utils import getToolByName
from Products.RhaptosRepository.Repository import Repository
from Products.RhaptosCollection.interfaces import ICollection

orig_publishRevision = Repository.publishRevision


def publishRevision(self, object, message):
    stool = getToolByName(self, 'portal_squid', None)
    if stool is None:
        orig_publishRevision(self, object, message)
        return

    ctool = getToolByName(self, 'content').catalog
    portal_url = getToolByName(self, 'portal_url')

    oldversion = None
    try:
	oldversion = object.getPublishedObject().latest.version
    except:
	pass

    orig_publishRevision(self, object, message)

    ob = object.getPublishedObject()

    # purge rss
    stool.pruneUrls(['content/recent.rss','content/collections.rss'])

    # always purge latest and previous version
    path = portal_url.getRelativeUrl(ob)
    paths = ['%s/latest/'%path]
    if oldversion:
        paths.append('%s/%s/'%(path, oldversion))
    
    if object.meta_type == "Module Editor":
	# purge all collection that reference this module
        cs = ctool({'containedModuleIds':ob.id,'portal_type':'Collection'})
	for c in cs:
	    p = c.getPath()[1:].split('/', 1)[-1]
	    paths.append('%s/'%p.rsplit('/latest')[0])
    elif ICollection.providedBy(object):
	# purge all latest modules that are part of this collection
	paths.extend(['content/%s/latest/'%m for m in object.containedModuleIds()])

    stool.pruneUrls(paths, 'PURGE_REGEXP')


Repository.publishRevision = publishRevision
