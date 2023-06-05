"""SAML Entity ID - Fix (Ray A.)"""

from urllib.parse import quote


class EntityIDMismatch(Exception):
    """Entity ID mismatch after update"""


class SAMLEidFix():
    """SAML Entity ID change fix"""

    auth_servers = '/api/v1/configuration/authentication/auth-servers'
    auth_server = '/api/v1/configuration/authentication/auth-servers/auth-server'
    saml_fqdn = '/api/v1/configuration/system/configuration/saml-configuration/settings/saml-fqdn'

    def __init__(self, host, rest_client) -> None:
        self.client = rest_client
        self.host = host
        self._auth_servers = []
        self._saml_servers = {}
        self._saml_fqdn = ''
        self._post_update = {}
        self._fetch_saml_fqdn()

    def _fetch_saml_fqdn(self):
        fqdn = self.client.get(f'https://{self.host}{self.saml_fqdn}')
        self._saml_fqdn = fqdn['saml-fqdn']

    def _fetch_auth_servers(self):
        servers = self.client.get(f'https://{self.host}{self.auth_servers}')
        self._auth_servers.extend(sorted([quote(server['name'])
                                          for server in servers['auth-server']]))

    def _filter_by_saml_type(self):
        for server in self._auth_servers:
            _ = self.client.get(
                f'https://{self.host}{self.auth_server}/{server}')
            if _['auth-server-type'] == 'saml':
                print(f"Found SAML server - # {_['name']} #")
                if _['saml']['settings']['host-fqdn'] == "":
                    print(f"*** {_['name']} *** has null host-fqdn value.\n")
                    self._saml_servers.update(
                        {server: {'name': _['name'], 'saml':
                                  {'settings': {
                                      'host-fqdn': self._saml_fqdn,
                                      'sa-entity-id': _['saml']['settings']['sa-entity-id']}}
                                  }})
                else:
                    print(
                        f"# {_['name']} # has valid host-fqdn value. Ignoring!\n")

    def start(self, dry_run: bool = False):
        """Start the SAML Eid update operation"""
        self._fetch_auth_servers()
        self._filter_by_saml_type()
        if dry_run:
            if self._saml_servers:
                print("^^^ DRY RUN: SAML servers with null host-fqdn value: ^^^\n")
                for server in self._saml_servers:
                    print(f"Name: {server}")
                    print(
                        f"Entity-ID: {server['saml']['settings']['sa-entity-id']}")
            else:
                print(
                    "^^^ DRY RUN: All SAML servers have valid host-fqdn value. No change required! ^^^\n")
        else:
            self._update_saml_fqdn()

    def _update_saml_fqdn(self):

        if self._saml_servers:
            print("Starting to update SAML host-fqdn values...\n")
            for server, data in self._saml_servers.items():
                self.client.put(
                    f'https://{self.host}{self.auth_server}/{server}', data=data)
                print(f"UPDATE_FQDN SUCCESS: SAML server - $ {server} $")
            self._validate()
        else:
            print("All SAML servers have valid host-fqdn value. No change required!\n")

    def _validate(self):
        """Validate the fix by comparing the fqdn & entity ID values post update"""
        for server in self._saml_servers:
            _ = self.client.get(
                f'https://{self.host}{self.auth_server}/{server}')
            print(f"\nValidating the fix for # {server} #")
            self._post_update.update(
                {server: {'name': _['name'], 'saml':
                          {'settings': {
                              'host-fqdn': _['saml']['settings']['host-fqdn'],
                              'sa-entity-id': _['saml']['settings']['sa-entity-id']}}
                          }})
        if self._saml_servers != self._post_update:
            self._print_eid_mismatch()
        else:
            print("\nValidation successful. Fix has been successfully applied.")

    def _print_eid_mismatch(self):
        """Print Entity ID mismatch results"""
        for server, eid in self._post_update.items():
            if self._saml_servers[server] != eid:
                print()
                print(f"NAME: {server}")
                print(
                    f"EXPECTED: {self._saml_servers[server]['saml']['settings']['sa-entity-id']}"
                )
                print(f"ACTUAL: {eid['saml']['settings']['sa-entity-id']}")
        raise EntityIDMismatch(
            "SAML Entity ID mismatch. Please revert the change using backup.")
