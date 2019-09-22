# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import os


def get_secret(id):
    if os.path.isfile("client_secrets.json"):
        secrets = json.loads(open("client_secrets.json").read())
        return secrets[id]
    else:
        raise IOError("No secrets file.")
