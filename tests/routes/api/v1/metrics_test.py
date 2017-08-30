# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.routes.api.v1.metrics import meeting_participants
from yelp_beans.routes.api.v1.metrics import meeting_requests
from yelp_beans.routes.api.v1.metrics import meeting_subscribers


def test_get_subscribers_none(app, minimal_database):
    with app.test_request_context('/v1/metrics/subscribers'):
        subscribed = json.loads(meeting_subscribers())
        assert subscribed == []


def test_get_subscribers(app, database, subscription, fake_user):
    with app.test_request_context('/v1/metrics/subscribers'):
        subscribed = json.loads(meeting_subscribers())
        assert subscribed == [{
            'title': 'Yelp Weekly',
            'subscriber': 'darwin@yelp.com'
        }]


def test_get_meeting_participants(app, database):
    pref = UserSubscriptionPreferences(subscription=database.sub.key, preference=database.prefs[0].key)
    pref.put()
    user1 = User(
        email='a@yelp.com',
        metadata={'department': 'dept'},
        subscription_preferences=[pref.key]
    )
    user1.put()
    user2 = User(
        email='b@yelp.com',
        metadata={'department': 'dept'},
        subscription_preferences=[pref.key]
    )
    user2.put()
    meeting1 = Meeting(meeting_spec=database.specs[0].key, cancelled=False).put()
    MeetingParticipant(meeting=meeting1, user=user1.key).put()
    MeetingParticipant(meeting=meeting1, user=user2.key).put()
    with app.test_request_context('/v1/metrics/meeting_participants'):
        participants = json.loads(meeting_participants())
        assert participants == [
            {
                'date': '2017-10-27T23:00:00',
                'meeting': 'agx0ZXN0YmVkLXRlc3RyDQsSB01lZXRpbmcYCgw',
                'meeting_title': 'Yelp Weekly',
                'participant': 'a@yelp.com',
                'time': '04:00PM'
            },
            {
                'date': '2017-10-27T23:00:00',
                'meeting': 'agx0ZXN0YmVkLXRlc3RyDQsSB01lZXRpbmcYCgw',
                'meeting_title': 'Yelp Weekly',
                'participant': 'b@yelp.com',
                'time': '04:00PM'
            }
        ]


def test_get_meeting_requests(app, database):
    pref = UserSubscriptionPreferences(subscription=database.sub.key, preference=database.prefs[0].key)
    pref.put()
    user = User(
        email='a@yelp.com',
        metadata={'department': 'dept'},
        subscription_preferences=[pref.key]
    )
    user.put()
    MeetingRequest(user=user.key, meeting_spec=database.specs[0].key).put()
    with app.test_request_context('/v1/metrics/meeting_requests'):
        requests = json.loads(meeting_requests())
    assert requests == [{
        'title': 'Yelp Weekly',
        'user': 'a@yelp.com'
    }]
