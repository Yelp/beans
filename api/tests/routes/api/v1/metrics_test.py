# -*- coding: utf-8 -*-
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.routes.api.v1.metrics import meeting_participants
from yelp_beans.routes.api.v1.metrics import meeting_requests
from yelp_beans.routes.api.v1.metrics import meeting_subscribers


def test_get_subscribers_none(app, session):
    with app.test_request_context('/v1/metrics/subscribers'):
        subscribed = meeting_subscribers().json
        assert subscribed == []


def test_get_subscribers(app, database, subscription, fake_user):
    with app.test_request_context('/v1/metrics/subscribers'):
        subscribed = meeting_subscribers().json
        assert subscribed == [{
            'title': 'Yelp Weekly',
            'subscriber': 'darwin@yelp.com'
        }]


def test_get_meeting_participants(app, database, session):
    pref = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    user1 = User(
        email='a@yelp.com',
        meta_data={'department': 'dept'},
        subscription_preferences=[pref]
    )
    user2 = User(
        email='b@yelp.com',
        meta_data={'department': 'dept'},
        subscription_preferences=[pref]
    )
    meeting1 = Meeting(meeting_spec=database.specs[0], cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting1, user=user1)
    mp2 = MeetingParticipant(meeting=meeting1, user=user2)

    session.add(pref)
    session.add(user1)
    session.add(user2)
    session.add(meeting1)
    session.add(mp1)
    session.add(mp2)
    session.commit()

    with app.test_request_context('/v1/metrics/meeting_participants'):
        participants = meeting_participants().json
        assert len(participants) == 2
        assert set(participants[0].keys()) == set(['date', 'meeting', 'meeting_title', 'participant', 'time'])
        assert participants[0]['date'] == database.specs[0].datetime.isoformat()

        participant_lookup = {participant['participant']: participant for participant in participants}

        assert participant_lookup[user1.email] == {
            'date': database.specs[0].datetime.isoformat(),
            'meeting': meeting1.id,
            'meeting_title': database.specs[0].meeting_subscription.title,
            'participant': user1.email,
            'time': '04:00PM',
        }


def test_get_meeting_requests(app, database, session):
    pref = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    user = User(
        email='a@yelp.com',
        meta_data={'department': 'dept'},
        subscription_preferences=[pref]
    )
    mr = MeetingRequest(user=user, meeting_spec=database.specs[0])

    session.add(pref)
    session.add(user)
    session.add(mr)
    session.commit()

    with app.test_request_context('/v1/metrics/meeting_requests'):
        requests = meeting_requests().json
    assert requests == [{
        'title': 'Yelp Weekly',
        'user': 'a@yelp.com'
    }]
