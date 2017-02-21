# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from yelp_beans.data_providers.data_provider import DataProvider


class JSONFileDataProvider(DataProvider):

    def __init__(self, path=None):
        self.path = path

    def ingest(self, data):
        data = self._load()
        employees = []
        for employee in data:
            user = {
                'email': employee.get('email'),
                'first_name': employee.get('first_name'),
                'last_name': employee.get('last_name'),
                'photo_url': employee.get('photo_url'),
            }
            remaining_keys = set(employee.keys()) - set(user.keys())
            user['metadata'] = {attr: employee[attr] for attr in remaining_keys}
            employees.append(user)

        return employees

    def _load(self):
        with open(self.path, 'rb') as json_file:
            data = json.load(json_file)
            return data
