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
        json_data = getUtility(IGroupSource, self.name)
        group = self.request.get('megaphone-group-%s' % self.name)
        if group and group in json_data.keys():
            return json_data[group]
        return []

    def all_groups(self):
        json_data = getUtility(IGroupSource, self.name)

        info = []
        for id_, entry in self.settings:
            if entry['recipient_type'] == self.name:
                for group in  entry['settingsdata']:
                    info.append({
                        'value': group,
                        'label': group,
                        'members': json_data[group]
                    })
        return info

    snippet = ViewPageTemplateFile('autocomplete_group_snippet.pt')

    def render_form(self):
        groups = self.all_groups()
        if len(groups):
            return self.snippet(groups=groups, script=self.script(),
                    name=self.name)
        return ''

    def script(self):
        return """
        $(document).ready(function () {
            $('#megaphone-group-%(name)s').autocomplete({
                source: %(source)s,
                focus: function(event, ui) {
                    $('#megaphone-group-%(name)s').val(ui.item.value);
                    $('#megaphone-group-members-%(name)s').html('');
                    $.each(ui.item.members, function(idx, val) {
                        $('#megaphone-group-members-%(name)s').append(
                            '<li>' + val.honorific + ' ' + 
                            val.first + ' ' + val.last + ' ' +
                            '(' + val.email + ') </li>'
                        );
                    });
                    return false
                },
                select: function(event, ui) {
                    $('#megaphone-group-%(name)s').val(ui.item.value);
                    $('#megaphone-group-members-%(name)s').html('');
                    $.each(ui.item.members, function(idx, val) {
                        $('#megaphone-group-members-%(name)s').append(
                            '<li>' + val.honorific + ' ' + 
                            val.first + ' ' + val.last + ' ' +
                            '(' + val.email + ') </li>'
                        );
                    });
                    return false
                },
                change: function(event, ui) {
                    $('#megaphone-group-%(name)s').val(ui.item.value);
                    $('#megaphone-group-members-%(name)s').html('');
                    $.each(ui.item.members, function(idx, val) {
                        $('#megaphone-group-members-%(name)s').append(
                            '<li>' + val.honorific + ' ' + 
                            val.first + ' ' + val.last + ' ' +
                            '(' + val.email + ') </li>'
                        );
                    });
                    return false
                }
            })
        })
        """ % {'source': json.dumps(self.all_groups()),
                'name': self.name}
