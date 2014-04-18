#!/bin/python

# http://www.webhelpdesk.com/api/
# http://docs.python-requests.org/en/latest/

import requests
from pprint import pprint

class WebHelpDesk(object):
    def __init__(self, helpdesk_url, apikey, ssl=True, debug=False):
        protocol = "https" if ssl else "http"
        self.debug = debug
        self.helpdesk_url = "%s://%s/helpdesk/WebObjects/Helpdesk.woa/ra" % (protocol, helpdesk_url)
        self.apikey = apikey
        self.auth = {'apiKey': self.apikey}
        
        # ToDo: Replace this with lazy load decorator:
        # http://stackoverflow.com/questions/3012421/python-lazy-property-decorator
        self._tickets = None
        self._billing_rates = None
        self._techs = None
        self._clients = None
        self._priority_types = None
        self._request_types = None
        self._status_types = None
        self._departments = None
        self._locations = None
        self._rooms = None
        self._bulk_actions = None
        self._custom_field_definitions = None
        self._setup = None
        self._assets = None
        self._asset_statuses = None
        self._asset_types = None
        self._manufacturers = None
        self._models = None

    def _api_request(self, path, args={}):
        url = "%s/%s" % (self.helpdesk_url, path)
        args['apiKey'] = self.apikey

        if self.debug:
            print "Url:", url
            print "Args", args
        result = requests.get(url, params=args)

        if self.debug:
            print "============="
            pprint(result.__dict__)
            print "============="

        if result.status_code != 200:
            self._handle_error(result)
            return []
        
        return result.json()

    def _handle_error(self, result):
        # Just print out the response object
        if self.debug:
            pprint(result.__dict__)
        else:
            return False

    def ticket(self, id):
        return self._api_request("Tickets/%d" % id)

    def tickets(self, closed=False, cancelled=False, resolved=False, deleted=False, qualifier=None):
        _qualifiers=[]
        if not closed:
            _qualifiers.append("(statustype.statusTypeName!='closed')")
        if not cancelled:
            _qualifiers.append("(statustype.statusTypeName!='cancelled')")
        if not resolved:
            _qualifiers.append("(statustype.statusTypeName!='resolved')")
        if not deleted:
            _qualifiers.append("(deleted!=1)")

        if qualifier is not None:
            qualifier = "((%s)and(%s))" % (qualifier, "and".join(_qualifiers))
        else:
            qualifier = "(%s)" % "and".join(_qualifiers)

        if self.debug:
            print "Using qualifier:", qualifier
        
        args = {'qualifier': qualifier,
                'limit': 100,
                'style': 'detailed',
                'page': 1}
        result = []
        result.append(self._api_request("Tickets", args=args))
        while len(result[args['page']-1]) == args['limit']:
            args['page'] += 1
            result.append(self._api_request("Tickets", args=args))

        return [ticket for page in result for ticket in page]

    def ticket_notes(self, id):
        args = {'jobTicketId': id}
        return self._api_request("TicketNotes", args=args)

    @property
    def billing_rates(self):
        if self._billing_rates is None:
            self._billing_rates = self._api_request("BillingRates")
        return self._billing_rates

    @property
    def techs(self):
        if self._techs is None:
            self._techs = self._api_request("Techs")
        return self._techs

    def tech(self, id):
        return self._api_request("Techs/%d" % id)

    @property
    def clients(self):
        if self._clients is None:
            self._clients = self._api_request("Clients")
        return self._clients

    def client(self, id):
        return self._api_request("Clients/%d" % id)

    @property
    def priority_types(self):
        if self._priority_types is None:
            self._priority_types = self._api_request("PriorityTypes")
        return self._priority_types

    @property
    def request_types(self):
        if self._request_types is None:
            self._request_types = self._api_request("RequestTypes")
        return self._request_types

    @property
    def status_types(self):
        if self._status_types is None:
            self._status_types = self._api_request("StatusTypes")
        return self._status_types

    @property
    def departments(self):
        if self._departments is None:
            self._departments = self._api_request("Departments")
        return self._departments

    def department(self, id):
        return self._api_request("Departments/%d" % id)

    @property
    def locations(self):
        if self._locations is None:
            self._locations = self._api_request("Locations")
        return self._locations

    def location(self, id):
        return self._api_request("Locations/%d" % id)

    @property
    def rooms(self):
        if self._rooms is None:
            self._rooms = self._api_request("Rooms")
        return self._rooms

    def room(self, id):
        return self._api_request("Rooms/%d" % id)

    @property
    def bulk_actions(self):
        if self._bulk_actions is None:
            self._bulk_actions = self._api_request("TicketBulkActions")
        return self._bulk_actions

    @property
    def custom_field_definitions(self):
        if self._custom_field_definitions is None:
            self._custom_field_definitions = self._api_request("CustomFieldDefinitions")
        return self._custom_field_definitions

    @property
    def setup(self):
        if self._setup is None:
            self._setup = self._api_request("Preferences")
        return self._setup

    @property
    def assets(self):
        if self._assets is None:
            self._assets = self._api_request("Assets")
        return self._assets

    @property
    def asset_statuses(self):
        if self._asset_statuses is None:
            self._asset_statuses = self._api_request("AssetStatuses")
        return self._asset_statuses

    @property
    def asset_types(self):
        if self._asset_types is None:
            self._asset_types = self._api_request("AssetTypes")
        return self._asset_types

    @property
    def manufacturers(self):
        if self._manufacturers is None:
            self._manufacturers = self._api_request("Manufacturers")
        return self._manufacturers

    @property
    def models(self):
        if self._models is None:
            self._models = self._api_request("Models")
        return self._models

    def test(self, debug=False):
        _current_debug = self.debug
        if self.debug and not debug:
            print "Disabling debug. Enable explicitly with helpdesk.test(debug=True)"
            self.debug = False

        print "Test List Retreval"
        print " tickets:", len(self.tickets())
        print " ticket_notes (ticket 1):", len(self.ticket_notes(1))
        print " billing_rates:", len(self.billing_rates)
        print " techs:", len(self.techs)
        print " clients:", len(self.clients)
        print " priority_types:", len(self.priority_types)
        print " request_types:", len(self.request_types)
        print " status_types:", len(self.status_types)
        print " departments:", len(self.departments)
        print " locations:", len(self.locations)
        print " rooms:", len(self.rooms)
        print " bulk_actions:", len(self.bulk_actions)
        print " custom_field_definitions:", len(self.custom_field_definitions)
        print " setup:", len(self.setup)
        print " assets:", len(self.assets)
        print " asset_statuses:", len(self.asset_statuses)
        print " asset_types:", len(self.asset_types)
        print " manufacturers:", len(self.manufacturers)
        print " models:", len(self.models)
        print
        print "Test Item Retreval"
        print " ticket 1:", len(self.ticket(1))
        print " tech 1:", len(self.tech(1))
        print " client 1:", len(self.client(1))
        print " department 1:", len(self.department(1))
        print " location 1:", len(self.location(1))
        print " room 1:", len(self.room(1))

        if _current_debug:
            "Turning debug back on"
            self.debug = True

