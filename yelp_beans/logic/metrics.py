# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

from yelp_beans.logic.meeting_spec import get_specs_for_current_week
from yelp_beans.logic.meeting_spec import get_users_from_spec
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import User


def get_subscribed_users():
    users = User.query().fetch()
    subscriptions = MeetingSubscription.query().fetch()

    metrics = defaultdict(set)
    # creates metrics keys for all subscriptions including ones without users
    for subscription in subscriptions:
        metrics[subscription.key.urlsafe()] = []

    # creates metrics keys for all subscriptions that have users with user data
    for user in users:
        for preference in user.subscription_preferences:
            metrics[preference.get().subscription.urlsafe()].append(user.email)

    return metrics


def get_current_week_participation():
    participation = defaultdict(dict)

    for spec in get_specs_for_current_week():
        participation[spec.meeting_subscription.urlsafe()][spec.key.urlsafe()] = [
            user.get_username() for user in filter(None, get_users_from_spec(spec))
        ]

    return participation
