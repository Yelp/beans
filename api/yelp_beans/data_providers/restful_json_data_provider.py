# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import requests
from requests.auth import HTTPBasicAuth
from yelp_beans.data_providers.data_provider import DataProvider


class RestfulJSONDataProvider(DataProvider):

    def __init__(self, url, username=None, password=None, timeout=60.0):
        self.url = url
        self.username = username
        self.password = password
        self.timeout = timeout

    def _authentication(self):
        if self.username and self.password:
            return HTTPBasicAuth(self.username, self.password)

    def _fetch(self, data):
        result = requests.get(
            self.url,
            auth=self._authentication(),
            timeout=self.timeout,
        )
        result.raise_for_status()
        return result.json()
