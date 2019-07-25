# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from pydoc import locate

from yelp_beans.logic.config import get_config


class DataIngestion(object):

    def __init__(self, *args, **kwargs):
        self.data_providers = []
        data_providers = get_config()['data_providers']
        for provider in data_providers:
            cls = locate(provider['class'])
            kwargs_keys = set(provider.keys()) - set(['class'])
            kwargs = {key: provider[key] for key in kwargs_keys}
            self.data_providers.append(cls(**kwargs))

    def ingest(self):
        data = None
        for provider in self.data_providers:
            data = provider.ingest(data)
        return data
