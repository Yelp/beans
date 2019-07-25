# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from flask import Blueprint
from flask import jsonify
from flask import request
from google.appengine.ext import ndb
from yelp_beans.logic.subscription import filter_subscriptions_by_user_data
from yelp_beans.logic.subscription import merge_subscriptions_with_preferences
from yelp_beans.logic.user import add_preferences
from yelp_beans.logic.user import get_user
from yelp_beans.logic.user import remove_preferences

preferences_blueprint = Blueprint('preferences', __name__)


@preferences_blueprint.route('/', methods=["GET"])
def preferences_api():
    user = get_user(request.args.get('email'))
    if not user:
        resp = jsonify([])
        resp.status_code = 200
        return resp

    subscriptions = merge_subscriptions_with_preferences(user)
    subscriptions = filter_subscriptions_by_user_data(subscriptions, user)

    resp = jsonify(subscriptions)
    resp.status_code = 200
    return resp


@preferences_blueprint.route('/subscription/<subscription>', methods=["POST"])
def preferences_api_post(subscription):
    data = request.json
    user = get_user(data.get('email'))
    del data['email']
    if not user:
        return '400'

    subscription_key = ndb.Key(urlsafe=subscription)
    form_selection = {}
    for key, value in data.items():
        form_selection[ndb.Key(urlsafe=key)] = value

    removed = remove_preferences(user, form_selection, subscription_key)
    logging.info('Removed')
    logging.info(removed)

    added = add_preferences(user, form_selection, subscription_key)
    logging.info('Added')
    logging.info(added)

    return 'OK'
