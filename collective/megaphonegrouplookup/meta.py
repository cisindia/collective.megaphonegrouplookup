from zope.interface import Interface
from zope import schema
from zope.component.zcml import adapter, utility
from collective.megaphonegrouplookup.manager_lookup import LookupRecipientSource as ManagerLRS
from collective.megaphonegrouplookup.user_lookup import LookupRecipientSource as UserLRS
from collective.megaphonegrouplookup.autocomplete_lookup import LookupRecipientSource as ACUserLRS
from collective.megaphonegrouplookup.autocomplete_group_lookup import LookupRecipientSource as ACGroupLRS
from collective.megaphonegrouplookup.common import LookupRecipientSourceRegistration

from collective.megaphonegrouplookup.interfaces import IGroupSource

from collective.megaphone.interfaces import IMegaphone
from zope.publisher.interfaces.browser import IBrowserRequest
from collective.megaphone.interfaces import IRecipientSource

from zope.configuration.fields import Path, GlobalObject
from zope.schema.vocabulary import SimpleVocabulary

import simplejson

class IDataSourceDirective(Interface):

    name = schema.TextLine(
        title=u'Name', 
        description=u'Identifier of the group',
    )

    json_source = Path(
        title=u'Name of the json file where the source is stored',
        description=u'''
            Refers to a file containing json in this format:

                {
                    'Group Title': [
                        {
                            'honorific': 'Mr',
                            'first': 'firstname',
                            'last': 'lastname',
                            'email': 'user@server.com',
                            'description': 'description'        
                        }, ...
                    ],
                    'Group Title': [
                        {
                            'honorific': 'Mr',
                            'first': 'firstname',
                            'last': 'lastname',
                            'email': 'user@server.com',
                            'description': 'description'        
                        }, ...
                    ]
                }
        '''
    )

    site = schema.TextLine(
        title=u'Site',
        description=u'Site ID',
        required=False,
    )

    title = schema.TextLine(
        title=u'Title',
        description=u'Title of the group',
        required=False,
    )

    description = schema.TextLine(
        title=u'Description',
        description=u'Description of the group',
        required=False
    )

    select_label = schema.TextLine(
        title=u'Label',
        description=u'Label of the selection field',
        required=False
    )

    select_description = schema.TextLine(
        title=u'Selection field description',
        required=False
    )

    form_label = schema.TextLine(
        title=u'Label in the form',
        required=False
    )


class ICustomDataSourceDirective(IDataSourceDirective):

    recipient_source = GlobalObject(
        title=u'Source',
        required=True
    )



def _register_datasource(_context, 
                        name, json_source, site,
                        title, description, 
                        select_label, select_description,
                        setting_iface,
                        adapter_factory,
                        label_getter=lambda x,y:y['settingsdata']):
    json_data = simplejson.loads(open(json_source).read())

    utility(_context, name=name, factory=lambda : json_data,
            provides=IGroupSource)
    utility_factory = type(str(name), (LookupRecipientSourceRegistration,), {
        'name': name,
        'title': title,
        'description': description,
        'site': site,
        'settings_schema': setting_iface, 
        'get_label': label_getter
    })

    utility(_context, name=name, factory=utility_factory)

    adapter(_context, factory=(adapter_factory,),
            for_=(IMegaphone, IBrowserRequest),
            provides=IRecipientSource,
            name=name)



def datasource_handler(_context, name, json_source, recipient_source, site=None, 
                            title=u'Officials by Group',
                            description=u'Looks up officials from a group list',
                            select_label=u'Group',
                            select_description=u'Please select a group',
                            form_label=u'Your letter will be sent to:'):

    if recipient_source==None:
        raise Exception('recipient source is not set')

    adapter_factory = type(str(name), (recipient_source,), {
        'name': name,
        'form_label': form_label,
    })

    json_data = simplejson.loads(open(json_source).read())

    vocab = SimpleVocabulary.fromItems([
                (i,i) for i in sorted(json_data.keys())
            ])


    class ISetting(Interface):
        settingsdata = schema.List(
            title=select_label,
            description=select_description,
            value_type=schema.Choice(
                vocabulary=vocab
            )
        )

    _register_datasource(_context,
                        name, json_source, site,
                        title, description,
                        select_label, select_description,
                        ISetting,
                        adapter_factory)


def managerdatasource_handler(_context, name, json_source, site=None, 
                            title=u'Officials by Group',
                            description=u'Looks up officials from a group list',
                            select_label=u'Group',
                            select_description=u'Please select a group',
                            form_label=u'Your letter will be sent to:'):

    datasource_handler(_context, name, json_source, 
            ManagerLRS,
            site, title, description, select_label, select_description,
            form_label)


def userdatasource_handler(_context, name, json_source, site=None,
                            title=u'Officials by Group : User selectible',
                            description=u'Looks up officials by group, selectible by user',
                            select_label=u'Groups',
                            select_description=u'Please select available groups',
                            form_label=u"Send To"
                            ):

    datasource_handler(_context, name, json_source, 
            UserLRS,
            site, title, description, select_label, select_description,
            form_label)

def autocomplete_userdatasource_handler(_context, name, json_source, site=None,
                            title=u'Officials by Group : User selects individual',
                            description=u'Looks up officials by group, selectible by user',
                            select_label=u'Officials',
                            select_description=u'Select official',
                            form_label=u"Send To"
                            ):

    datasource_handler(_context, name, json_source,
            ACUserLRS,
            site, title, description, select_label, select_description,
            form_label)


def autocomplete_groupdatasource_handler(_context, name, json_source, site=None,
                            title=u'Officials by Group : User selects group',
                            description=u'Looks up officials by group, selectible by user',
                            select_label=u'Groups',
                            select_description=u'Select group',
                            form_label=u"Send To"
                            ):


    datasource_handler(_context, name, json_source,
            ACGroupLRS,
            site, title, description, select_label, select_description,
            form_label)
