# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from yelp_beans.logic.secret import get_secret


class DataProvider(object):
    # TODO: docs

    def load_secrets(self):
        logging.info("Loading secrets: {}".format(self.secrets))
        return [get_secret(name) for name in self.secrets]

    def fetch(self):
        return None

    def munge(self, data):
        return data

    def __call__(self):
        return self.munge(self.fetch(*self.load_secrets()))
