# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class DataProvider(object):

    def ingest(self, data=None):
        raw_data = self._fetch(data)
        return self._parse(raw_data)

    def _fetch(self, data):
        raise NotImplementedError

    def _parse(self, data):
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
