# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from datetime import timedelta

from yelp_beans.matching.group_match import generate_group_meetings
from yelp_beans.matching.group_match import generate_groups
from yelp_beans.matching.group_match import get_previous_meetings_counts
from yelp_beans.matching.group_match import get_user_weights
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


MEETING_COOLDOWN_WEEKS = 10


def test_generate_groups():
    result = generate_groups([], 3)
    assert [x for x in result] == []

    result = generate_groups([1], 3)
    assert [x for x in result] == [[1]]

    result = generate_groups([1, 2, 3, 4, 5], 3)
    assert [x for x in result] == [[1, 2, 3], [4, 5]]

    result = generate_groups([1, 2, 3, 4], 2)
    assert [x for x in result] == [[1, 2], [3, 4]]


def test_generate_group_meetings_invalid_number_of_users(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='b@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting, user=user2)
    mp2 = MeetingParticipant(meeting=meeting, user=user1)

    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(user1)
    session.add(user2)
    session.add(meeting_spec)
    session.add(meeting)
    session.add(mp1)
    session.add(mp2)
    session.commit()

    matched, unmatched = generate_group_meetings([], meeting_spec, 3, 10, 5)
    assert matched == []
    assert unmatched == []

    matched, unmatched = generate_group_meetings([user1], meeting_spec, 3, 10, 5)
    assert matched == []
    assert unmatched == [user1]

    matched, unmatched = generate_group_meetings([user1, user2], meeting_spec, 3, 10, 5)
    assert matched == []
    assert set(unmatched) == {user1, user2}


def test_generate_group_meetings(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='b@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    user3 = User(email='c@yelp.com', meta_data={'department': 'dept3'}, subscription_preferences=[user_pref])
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting, user=user3)
    mp2 = MeetingParticipant(meeting=meeting, user=user2)
    mp3 = MeetingParticipant(meeting=meeting, user=user1)

    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(user1)
    session.add(user2)
    session.add(user3)
    session.add(meeting_spec)
    session.add(meeting)
    session.add(mp1)
    session.add(mp2)
    session.add(mp3)
    session.commit()

    matched, unmatched = generate_group_meetings([user1, user2, user3], meeting_spec, 3, 10, 5)
    assert {user for user in matched[0]} == {user1, user2, user3}
    assert unmatched == []


def test_get_previous_meetings_counts(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='b@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting, user=user2)
    mp2 = MeetingParticipant(meeting=meeting, user=user1)

    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(user1)
    session.add(user2)
    session.add(meeting_spec)
    session.add(meeting)
    session.add(mp1)
    session.add(mp2)
    session.commit()

    assert(get_previous_meetings_counts([user1, user2], subscription) == {(user1.id, user2.id): 1})


def test_get_user_weights(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='b@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting, user=user2)
    mp2 = MeetingParticipant(meeting=meeting, user=user1)

    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(user1)
    session.add(user2)
    session.add(meeting_spec)
    session.add(meeting)
    session.add(mp1)
    session.add(mp2)
    session.commit()

    previous_meetings_count = get_previous_meetings_counts([user1, user2], subscription)

    assert(get_user_weights([user1, user2], previous_meetings_count, 10, 5) == [[0, 5], [5, 0]])
