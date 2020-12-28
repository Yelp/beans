# -*- coding: utf-8 -*-
import yaml


# TODO: Formalize output and validate schema
def get_config():
    with open('config.yaml') as config_file:
        config = yaml.safe_load(config_file)
        return config
