"""HTTP Auth Manager - urllib (Ray A.)"""

from urllib.request import HTTPBasicAuthHandler, HTTPPasswordMgrWithPriorAuth


class HTTPAuthMgr():
    """HTTP Auth for REST Client"""

    def __init__(self, uri, username: str, password: str) -> None:
        self.passwdmgr = HTTPPasswordMgrWithPriorAuth()
        self.passwdmgr.add_password(
            realm=None, uri=f"https://{uri}", user=username, passwd=password, is_authenticated=True)
        self._init_basicauth()

    def _init_basicauth(self):
        self.auth = HTTPBasicAuthHandler(self.passwdmgr)

    @property
    def authmgr(self):
        """Get Auth Manager"""
        return self.auth
