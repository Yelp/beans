# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from flask import Blueprint
from flask import request

from yelp_beans.logic.user import get_user

user_blueprint = Blueprint('user', __name__)


@user_blueprint.route('/', methods=["GET"])
def user_api():
    user = get_user(request.args.get('email'))
    if not user:
        return json.dumps({})

    return json.dumps({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'photo_url': user.photo_url,
        'metadata': user.metadata
    })
