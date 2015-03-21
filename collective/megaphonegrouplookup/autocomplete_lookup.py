import logging
from zope import schema
from zope.interface import Interface
from zope.component import getUtility
from zope.app.component.hooks import getSite
from zope.interface import implements
from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from collective.megaphone.interfaces import (IRecipientSource,
                                                     IRecipientSourceRegistration)
from collective.megaphone.recipients import (get_recipient_settings,
                                                     recipient_label)
from Products.CMFCore.utils import getToolByName

from zope.component import getUtility

from collective.megaphonegrouplookup.interfaces import IGroupSource
import json


class LookupRecipientSource(object):
    implements(IRecipientSource)

    name = 'group_autocomplete_recipient_lookup'
    form_label = 'Send to'

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.settings = get_recipient_settings(context, self.name)

    def lookup(self):
        info = []
        person = self.request.get('megaphone-person-email')
        for entry in self.all_entries():
            if entry['email'] == person:
                info.append(entry)
        return info

    def all_entries(self):
        json_data = getUtility(IGroupSource, self.name)

        info = []
        for id_, entry in self.settings:
            if entry['recipient_type'] == self.name:
                for group in entry['settingsdata']:
                    info += json_data[group]
        return info

    snippet = ViewPageTemplateFile('autocomplete_snippet.pt')

    def render_form(self):
        recipients = [r for r in  self.all_entries()]
        if len(recipients):
            return self.snippet(recipients=recipients, script=self.script())
        return ''

    def script(self):
        return """

        $(document).ready(function () {
            $('#megaphone-person-ac').autocomplete({
                source: %s,
                focus: function (event, ui) {
                    $('#megaphone-person-ac').val(ui.item.label);
                    $('#megaphone-person-email').val(ui.item.value);
                    $('#megaphone-person-address').show();
                    $('#megaphone-person-address').html(ui.item.address);
                    return false
                },
                select: function(event, ui) {
                    $('#megaphone-person-ac').val(ui.item.label);
                    $('#megaphone-person-email').val(ui.item.value);
                    $('#megaphone-person-address').show();
                    $('#megaphone-person-address').html(ui.item.address);
                    return false
                },
                change: function (event, ui) {
                    $('#megaphone-person-ac').val(ui.item.label);
                    $('#megaphone-person-email').val(ui.item.value);
                    $('#megaphone-person-address').show();
                    $('#megaphone-person-address').html(ui.item.address);
                    return false
                }
            })
        })
        """ % json.dumps([{
                'label': ' '.join([i['honorific'], i['first'], i['last']]),
                'value': i['email'],
                'address': ('Present Address\n%s\n\nPermanent Address\n%s' % (
                    i['Present Address'], 
                    i['Permanent Address'])
                ).replace('\n','<br/>')
            } for i in self.all_entries()])

