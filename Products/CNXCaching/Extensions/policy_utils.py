from Products.CacheSetup import config
from Products.CNXCaching.Extensions import policy


def addCachePolicies(portal, out):
    # We'll extend this later
    # preferably using GenericSetup profiles
    ct = getattr(portal, config.CACHE_TOOL_ID)
    # fix any id collisions
    if getattr(ct, policy.POLICY_ID, None) is not None:
        ct.manage_delObjects([policy.POLICY_ID])
    # now add the new policy
    ct.addPolicyFolder(policy.POLICY_ID, policy.POLICY_TITLE)
    rules = ct.getRules(policy.POLICY_ID)
    policy.addCacheRules(rules)
    header_sets = ct.getHeaderSets(policy.POLICY_ID)
    policy.addHeaderSets(header_sets)
    # Lets move the new policies to the top of the list
    policy_ids = [policy.POLICY_ID]
    ct.moveObjectsToTop(policy_ids)
