# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from datetime import datetime
from datetime import timedelta

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
    result = generate_groups([1, 2, 3, 4, 5], 3)
    assert [x for x in result] == [[1, 2, 3], [4, 5]]

    result = generate_groups([1, 2, 3, 4], 2)
    assert [x for x in result] == [[1, 2], [3, 4]]


def test_get_previous_meetings_counts(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref]).put()
    user2 = User(email='b@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref]).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime).put()
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False).put()
    MeetingParticipant(meeting=meeting, user=user2).put()
    MeetingParticipant(meeting=meeting, user=user1).put()

    assert(get_previous_meetings_counts([user1.get(), user2.get()], subscription) == {(user1.id(), user2.id()): 1})


def test_get_user_weights(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref]).put()
    user2 = User(email='b@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref]).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime).put()
    meeting = Meeting(meeting_spec=meeting_spec, cancelled=False).put()
    MeetingParticipant(meeting=meeting, user=user2).put()
    MeetingParticipant(meeting=meeting, user=user1).put()
    previous_meetings_count = get_previous_meetings_counts([user1.get(), user2.get()], subscription)

    assert(get_user_weights([user1.get(), user2.get()], previous_meetings_count, 10, 5) == [[0, 5], [5, 0]])
