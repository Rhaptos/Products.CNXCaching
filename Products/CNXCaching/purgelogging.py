""" monkey patch for logging purge urls """
import logging, traceback
from Products.CMFSquidTool import utils, SquidTool, queue

logger = logging.getLogger('CNXCaching')

origPruneUrl = utils.pruneUrl
origPruneAsync = utils.pruneAsync


def pruneUrl(url, purge_type='PURGE'):
    logger.info('pruneUrl: %s, %s', url, purge_type)

    # somtimes it usefull to see code execution stack
    # this helps to find who cause a purge
    #traceback.print_stack()

    origPruneUrl(url, purge_type)


def pruneAsync(url, purge_type='PURGE', daemon=True):
    logger.info('pruneAsync: %s, %s', url, purge_type)

    # somtimes it usefull to see code execution stack
    # this helps to find who cause a purge
    #traceback.print_stack()

    origPruneAsync(url, purge_type, daemon)

utils.pruneUrl = pruneUrl
utils.pruneAsync = pruneAsync
SquidTool.pruneUrl = pruneUrl
SquidTool.pruneAsync = pruneAsync
queue.pruneUrl = pruneUrl
queue.pruneAsync = pruneAsync


logger.info("Monkey patch Products.SquidTool.utils.pruneXXX, adding purge logging")


def pruneUrls(self, ob_urls=None, purge_type="PURGE", REQUEST=None):
        # ob_url is a relative to portal url 

        results = []
        purge_urls = self.squid_urls
        if ob_urls:
            purge_urls = self.computePurgeUrls(ob_urls)
        
        for url in purge_urls:
            # If a response was given, we do it synchronously and write the 
            # results to the response.  Otherwise we just queue it up. 
            if REQUEST:
                status, xcache, xerror = pruneUrl(url, purge_type)
            
                # NOTE: if the purge was successfull status will be 200 (OK) 
                #       if the object was not in cache status is 404 (NOT FOUND) 
                #       if you are not allowed to PURGE status is 403 
                REQUEST.RESPONSE.write('%s\t%s\t%s\n' % (status, url, xerror or xcache))
            else:
                pruneAsync(url, purge_type)
                status = "Queued"
                xcache = xerror = ""
            results.append((status, xcache, xerror))

        return results


SquidTool.pruneUrls = pruneUrls
