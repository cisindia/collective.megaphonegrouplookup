from Products.Five import BrowserView
from zope.component import getUtility
from collective.megaphonegrouplookup.interfaces import IGroupSource

class MegaphoneLookupUtil(BrowserView):
    def enable_orderedlist_js(self):
        # hack to check whether currently its megaphone view
        url = self.request.get('URL')
        if url.endswith('addMegaphoneAction'):
            return True
        if url.endswith('editMegaphoneAction'):
            return True
        return False


    def lookup_data(self, name, key):
        json_data = getUtility(IGroupSource, name)
        if key in json_data.keys():
            return json_data[key]
        return []
