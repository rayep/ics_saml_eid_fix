"""REST Client - urllib (Ray A.)"""

from urllib.request import (
    Request,
    build_opener,
    ProxyHandler)
import json


class RESTClient():
    """REST Client"""

    def __init__(self, auth_manager, proxy=None) -> None:
        self.auth = auth_manager.authmgr
        self.proxy = ProxyHandler(proxy) if proxy else None
        self.session = build_opener(
            self.proxy, self.auth) if self.proxy else build_opener(self.auth)

    def _create_request(self, url: str, method: str, data: str = None):
        request = Request(url, json.dumps(data).encode('utf-8'), method=method) \
            if data else Request(url, method=method)
        if isinstance(data, dict):
            request.add_header('Content-Type', 'application/json; charset=utf-8')
        request.timeout = 10
        with self.session.open(request) as response:
            return json.loads(response.read().decode())

    def get(self, url):
        """HTTP GET"""
        return self._create_request(url, method='GET')

    def put(self, url, data):
        """HTTP PUT"""
        return self._create_request(url, data=data, method='PUT')
