# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from six import with_metaclass

from yelp_beans import data_provider_map
from yelp_beans.logic.secret import get_secret


def _register_data_provider(data_provider_cls):
    data_provider_map[data_provider_cls.__name__] = data_provider_cls


class DataProviderType(type):

    def __new__(cls, *args, **kwargs):
        _cls = super(DataProviderType, cls).__new__(cls, *args, **kwargs)
        _register_data_provider(_cls)
        return _cls


class DataProvider(with_metaclass(DataProviderType)):

    def load_secrets(self):
        logging.info("Loading secrets: {}".format(self.secrets))
        return [get_secret(name) for name in self.secrets]

    def fetch(self):
        return None

    def munge(self, data):
        return data

    def __call__(self):
        return self.munge(self.fetch(*self.load_secrets()))
