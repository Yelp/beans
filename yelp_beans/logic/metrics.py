# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict

from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.meeting_spec import get_specs_for_current_week
from yelp_beans.logic.meeting_spec import get_users_from_spec
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import User


def get_subscribers():
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


def get_meeting_participants():
    meetings = defaultdict(list)
    participants = MeetingParticipant.query().fetch()
    for participant in participants:
        try:
            email = participant.user.get().email
            meeting = participant.meeting
            meetings[meeting].append(email)
        except AttributeError:
            pass

    metrics = []
    for meeting_key in meetings.keys():
        meeting_spec = meeting_key.get().meeting_spec.get()
        meeting_title = meeting_spec.meeting_subscription.get().title
        participants = meetings[meeting_key]
        for participant in participants:
            metrics.append(
                {
                    'participant': participant,
                    'meeting': meeting_key.urlsafe(),
                    'meeting_title': meeting_title,
                    'date': meeting_spec.datetime.isoformat(),
                    'time': get_meeting_datetime(meeting_spec).strftime('%I:%M%p'),
                }
            )
    return metrics


def get_meeting_requests():
    requests = []
    for spec in get_specs_for_current_week():
        users = [
            request.user.get().email
            for request
            in MeetingRequest.query(
                MeetingRequest.meeting_spec == spec.key
            ).fetch()
        ]
        for user in users:
            requests.append(
                {
                    'title': spec.meeting_subscription.get().title,
                    'user': user,
                }
            )
    return requests
