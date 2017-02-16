# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
from google.appengine.ext import ndb

from flask import Blueprint

from yelp_beans.models import Meeting
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import UserSubscriptionPreferences

metrics_blueprint = Blueprint('metrics', __name__)


@metrics_blueprint.route('/', methods=['GET'])
def metrics_api():
    keys_only = ndb.QueryOptions(keys_only=True)

    meeting_subscriptions = MeetingSubscription.query().fetch()
    metrics = []
    for subscription in meeting_subscriptions:
        data = {
            'title': subscription.title,
            'subscribed': UserSubscriptionPreferences.query(
                UserSubscriptionPreferences.subscription == subscription.key
            ).count(options=keys_only),
            'meetings': Meeting.query().count(options=keys_only),
        }
        metrics.append(data)
    return json.dumps(metrics)
