"""SAML Entity ID - Fix (Ray A.)"""

from urllib.parse import quote


class SAMLEidFix():
    """SAML Entity ID change fix"""

    auth_servers = '/api/v1/configuration/authentication/auth-servers'
    auth_server = '/api/v1/configuration/authentication/auth-servers/auth-server'
    saml_fqdn = '/api/v1/configuration/system/configuration/saml-configuration/settings/saml-fqdn'

    def __init__(self, host, rest_client) -> None:
        self.client = rest_client
        self.host = host
        self._auth_servers = []
        self.saml_servers = {}
        self._saml_fqdn = ''
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
                    self.saml_servers.update(
                        {server: {'name': _['name'], 'saml':
                                  {'settings': {
                                      'host-fqdn': self._saml_fqdn,
                                      'sa-entity-id': _['saml']['settings']['sa-entity-id']}}
                                  }})
                else:
                    print(
                        f"# {_['name']} # has a valid host-fqdn value. Ignoring!\n")

    def start(self, dry_run: bool = False):
        """Start the SAML Eid update operation"""
        self._fetch_auth_servers()
        self._filter_by_saml_type()
        if dry_run:
            if self.saml_servers:
                print("DRY RUN: SAML servers with null host-fqdn value:\n")
                for server in self.saml_servers:
                    print(server)
            else:
                print(
                    "DRY RUN: All SAML servers have valid host-fqdn value. No change required!\n")
        else:
            self._update_saml_fqdn()

    def _update_saml_fqdn(self):

        if self.saml_servers:
            print("Starting to update SAML host-fqdn values...\n")
            for server, data in self.saml_servers.items():
                self.client.put(
                    f'https://{self.host}{self.auth_server}{server}', data=data)
                print(f"UPDATE_FQDN SUCCESS: SAML server - $ {server} $")
        else:
            print("All SAML servers have valid host-fqdn value. No change required!\n")
