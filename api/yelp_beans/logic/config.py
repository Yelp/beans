# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import yaml


# TODO: Formalize output and validate schema
def get_config():
    with open('config.yaml') as config_file:
        config = yaml.safe_load(config_file)
        return config
