""" """
import logging
from StringIO import StringIO
from Products.CMFCore.utils import getToolByName
from Products.CNXCaching.config import PROJECTNAME, GLOBALS
from Products.CNXCaching.Extensions import policy_utils

logger = logging.getLogger('%s.Install' % PROJECTNAME)
def log(msg, out=None):
    logger.info(msg)
    if out: print >> out, msg
    print msg

def install(self, reinstall=False):
    """Install method for this product. Runs GenericSetup application. If you do anything
    else, be sure to note that QuickInstaller is the only method available for install in
    the README.

    It should be kept idempotent; running it at any time should be safe. Also, necessary
    upgrades to existing data should be accomplished with a reinstall (running this!) if
    at all possible.
    """
    out = StringIO()
    log("Starting %s install" % PROJECTNAME, out)

    urltool = getToolByName(self, 'portal_url')
    portal = urltool.getPortalObject()

    # setup tool prep
    setup_tool = getToolByName(portal, 'portal_setup')
    prevcontext = setup_tool.getImportContextID()
    setup_tool.setImportContext('profile-CMFPlone:plone')   # get Plone steps registered, in case they're not
    setup_tool.setImportContext('profile-Products.%s:default' % PROJECTNAME)  # our profile and steps

    # run all import steps
    status = setup_tool.runAllImportSteps()
    log(status['messages'], out)

    # setup tool "teardown"
    setup_tool.setImportContext(prevcontext)

    # add new cache policies
    policy_utils.addCachePolicies(self, out)

    log("Successfully installed %s." % PROJECTNAME, out)
    return out.getvalue()
