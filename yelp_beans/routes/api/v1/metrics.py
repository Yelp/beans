# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from flask import Blueprint

from yelp_beans.logic.metrics import get_current_week_participation
from yelp_beans.logic.metrics import get_subscribed_users
from yelp_beans.models import MeetingSubscription


metrics_blueprint = Blueprint('metrics', __name__)


@metrics_blueprint.route('/', methods=['GET'])
def metrics_api():
    metrics = []
    subscribed_users = get_subscribed_users()
    participation = get_current_week_participation()
    subscriptions = MeetingSubscription.query().fetch()

    for subscription in subscriptions:
        metric = {
            'key': subscription.key.urlsafe(),
            'title': subscription.title,
            'subscribed': subscribed_users[subscription.key.urlsafe()],
            'total_subscribed': len(subscribed_users[subscription.key.urlsafe()]),
            'week_participants': sum(
                len(spec) for spec in
                participation.get(subscription.key.urlsafe(), {}).values()
            ),
        }
        metrics.append(metric)
    return json.dumps(metrics)
