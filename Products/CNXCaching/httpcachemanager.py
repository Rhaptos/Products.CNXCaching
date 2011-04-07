import logging
from Products.CMFCore.utils import getToolByName
from Products.CacheSetup.content.cache_tool import CacheTool
from Products.PolicyHTTPCacheManager.PolicyHTTPCacheManager import PolicyHTTPCache

logger = logging.getLogger('CNXCaching')


def ZCache_invalidate(self, ob):
    # Note that this only works for default views of objects. 
    st = getToolByName(ob, 'portal_squid', None)
    if st is None:
        return 'Squid Tool not found, invalidation ignored.'

    #try:
	#if 'CNX' not in ob.meta_type:
	#    results = st.pruneObject(ob)
    #except:
	#pass

    results = []
    phys_path = ob.getPhysicalPath()
    
    if self.hit_counts.has_key(phys_path):
        del self.hit_counts[phys_path]
    results = ['\t'.join(map(str, line)) for line in results]
    return 'Server response(s): ' + ';'.join(results)


PolicyHTTPCache.ZCache_invalidate = ZCache_invalidate
logger.info("Monkey patch PolicyHTTPCacheManager.ZCache_invalidate, disable purges for cnx files")


orig_getUrlsToPurge = CacheTool.getUrlsToPurge

def getUrlsToPurge(self, object):
    try:
	return orig_getUrlsToPurge(self, object)
    except:
	return []
	
logger.info("Monkey patch CacheTool.getUrlsToPurge, handle all exceptions")
