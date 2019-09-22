# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from yelp_beans.logic.metrics import get_meeting_participants
from yelp_beans.logic.metrics import get_meeting_requests
from yelp_beans.logic.metrics import get_subscribers
from yelp_beans.models import MeetingSubscription


metrics_blueprint = Blueprint('metrics', __name__)


@metrics_blueprint.route('/subscribers', methods=['GET'])
def meeting_subscribers():
    metrics = []
    subscribed_users = get_subscribers()
    subscriptions = MeetingSubscription.query().fetch()

    for subscription in subscriptions:
        subscribed = set(subscribed_users[subscription.key.urlsafe()])

        for subscriber in subscribed:
            metrics.append(
                {
                    'title': subscription.title,
                    'subscriber': subscriber,
                }
            )
    resp = jsonify(metrics)
    resp.status_code = 200
    return resp


@metrics_blueprint.route('/meetings', methods=['GET'])
def meeting_participants():
    resp = jsonify(get_meeting_participants())
    resp.status_code = 200
    return resp


@metrics_blueprint.route('/requests', methods=['GET'])
def meeting_requests():
    resp = jsonify(get_meeting_requests())
    resp.status_code = 200
    return resp
