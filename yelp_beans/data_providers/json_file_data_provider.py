# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from yelp_beans.data_providers.data_provider import DataProvider


class JSONFileDataProvider(DataProvider):

    def __init__(self, path=None):
        self.path = path

    def _fetch(self, data):
        with open(self.path, 'rb') as json_file:
            data = json.load(json_file)
            return data
