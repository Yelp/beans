# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from datetime import timedelta

from yelp_beans.matching.match import generate_meetings
from yelp_beans.matching.match_utils import get_counts_for_pairs
from yelp_beans.matching.match_utils import get_previous_meetings
from yelp_beans.matching.match_utils import save_meetings
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences

MEETING_COOLDOWN_WEEKS = 10


def test_pair_to_counts():
    pairs = [('user1', 'user2'), ('user1', 'user2'), ('user2', 'user3')]
    counts = get_counts_for_pairs(pairs)
    assert (counts[('user2', 'user3')] == 1)
    assert(counts[('user1', 'user2')] == 2)


def test_generate_save_meetings(minimal_database, subscription):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref]).put()
    user2 = User(email='b@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref]).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime)
    meeting_spec.put()
    MeetingRequest(user=user1, meeting_spec=meeting_spec.key).put()
    MeetingRequest(user=user2, meeting_spec=meeting_spec.key).put()

    matches, unmatched = generate_meetings([user1.get(), user2.get()], meeting_spec)
    save_meetings(matches, meeting_spec)

    assert unmatched == []

    participants = [
        participant.user
        for participant in MeetingParticipant.query().fetch()
    ]

    assert participants == [user1, user2]


def test_get_previous_meetings(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref]).put()
    user2 = User(email='a@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref]).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime).put()
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False).put()
    MeetingParticipant(meeting=meeting, user=user2).put()
    MeetingParticipant(meeting=meeting, user=user1).put()

    assert get_previous_meetings(subscription) == set([(user1.id(), user2.id())])


def test_get_previous_meetings_multi_subscription(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription1 = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    subscription2 = MeetingSubscription(title='all sales weekly', datetime=[pref_1]).put()
    user_pref1 = UserSubscriptionPreferences(preference=pref_1, subscription=subscription1).put()
    user_pref2 = UserSubscriptionPreferences(preference=pref_1, subscription=subscription2).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref1, user_pref2]).put()
    user2 = User(email='a@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref1, user_pref2]).put()
    meeting_spec1 = MeetingSpec(meeting_subscription=subscription1, datetime=pref_1.get().datetime).put()
    meeting = Meeting(meeting_spec=meeting_spec1, cancelled=False).put()
    MeetingParticipant(meeting=meeting, user=user2).put()
    MeetingParticipant(meeting=meeting, user=user1).put()

    assert get_previous_meetings(subscription1) == set([(user1.id(), user2.id())])
    assert get_previous_meetings(subscription2) == set([])


def test_get_previous_multi_meetings(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref]).put()
    user2 = User(email='a@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref]).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime).put()
    meeting1 = Meeting(meeting_spec=meeting_spec, cancelled=False).put()
    meeting2 = Meeting(meeting_spec=meeting_spec, cancelled=False).put()
    MeetingParticipant(meeting=meeting1, user=user2).put()
    MeetingParticipant(meeting=meeting1, user=user1).put()
    MeetingParticipant(meeting=meeting2, user=user2).put()
    MeetingParticipant(meeting=meeting2, user=user1).put()

    assert get_previous_meetings(subscription) == set([(user1.id(), user2.id()), (user1.id(), user2.id())])


def test_get_previous_meetings_no_specs(database_no_specs):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS + 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref]).put()
    user2 = User(email='a@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref]).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime).put()
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False).put()
    MeetingParticipant(meeting=meeting, user=user2).put()
    MeetingParticipant(meeting=meeting, user=user1).put()

    assert get_previous_meetings(subscription) == set([])
