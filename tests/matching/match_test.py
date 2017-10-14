# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import itertools
from datetime import datetime
from datetime import timedelta

from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.matching.match import generate_meetings
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


MEETING_COOLDOWN_WEEKS = 10


def test_generate_meetings_same_department(minimal_database, subscription):
    rule = Rule(name='department', value='').put()
    subscription.dept_rules = [rule]
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(preference=preference, subscription=subscription.key).put()
    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user1.put()
    user2 = User(email='b@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user2.put()
    user_list = [user1, user2]

    _, specs = get_specs_from_subscription(subscription)
    matches, unmatched = generate_meetings(user_list, specs[0])
    assert len(unmatched) == 2
    assert len(matches) == 0


def test_generate_meetings_with_history(minimal_database, subscription):
    rule = Rule(name='department', value='').put()
    subscription.dept_rules = [rule]

    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(preference=preference, subscription=subscription.key).put()

    user1 = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user1.put()
    user2 = User(email='b@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref])
    user2.put()
    user3 = User(email='c@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user3.put()
    user4 = User(email='d@yelp.com', metadata={'department': 'dept2'}, subscription_preferences=[user_pref])
    user4.put()

    user_list = [user1, user2, user3, user4]
    week_start, specs = get_specs_from_subscription(subscription)
    store_specs_from_subscription(subscription.key, week_start, specs)

    matches, unmatched = generate_meetings(user_list, specs[0])
    assert len(matches) == 2
    assert len(unmatched) == 0

    meeting_history = set([
        (user1.key.id(), user2.key.id()),
        (user3.key.id(), user4.key.id()),
        (user2.key.id(), user3.key.id()),
        (user1.key.id(), user4.key.id()),
    ])
    matches, unmatched = generate_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 0
    assert len(unmatched) == 4

    meeting_history = set([
        (user1.key.id(), user2.key.id()),
        (user3.key.id(), user4.key.id()),
        (user2.key.id(), user3.key.id()),
    ])
    matches, unmatched = generate_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 1
    assert len(unmatched) == 2


def test_no_re_matches(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime)
    meeting_spec.put()

    users = []
    num_users = 20
    for i in range(0, num_users):
        user = User(email='{}@yelp.com'.format(i), metadata={
                    'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref])
        user.put()
        MeetingRequest(user=user.key, meeting_spec=meeting_spec.key).put()
        users.append(user)

    previous_meetings = {pair for pair in itertools.combinations([user.key.id() for user in users], 2)}
    previous_meetings = previous_meetings - {(users[0].key.id(), users[1].key.id())}
    matches, unmatched = generate_meetings(users, meeting_spec, previous_meetings)
    assert len(unmatched) == num_users - 2
    assert [(match[0].key.id(), match[1].key.id()) for match in matches] == [(users[0].key.id(), users[1].key.id())]


def test_generate_group_meeting(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime)
    meeting_spec.put()

    users = []
    num_users = 21
    for i in range(0, num_users):
        user = User(email='{}@yelp.com'.format(i), metadata={
                    'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref])
        user.put()
        MeetingRequest(user=user.key, meeting_spec=meeting_spec.key).put()
        users.append(user)

    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=3)
    assert(len(matches) == 7)
    assert (len(unmatched) == 0)
    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=5)
    assert(len(matches) == 4)
    assert (len(unmatched) == 1)


def test_generate_group_meeting_invalid_number_of_users(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1]).put()
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime)
    meeting_spec.put()

    users = []
    for i in range(0, 2):
        user = User(email='{}@yelp.com'.format(i), metadata={
            'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref])
        user.put()
        MeetingRequest(user=user.key, meeting_spec=meeting_spec.key).put()
        users.append(user)

    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=3)
    assert(len(matches) == 0)
    assert (len(unmatched) == 2)


def test_previous_meeting_penalty(minimal_database):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1)).put()
    pref_2 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 2)).put()
    pref_3 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 3)).put()
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1, pref_2, pref_3]).put()
    user_pref1 = UserSubscriptionPreferences(preference=pref_1, subscription=subscription).put()
    user_pref2 = UserSubscriptionPreferences(preference=pref_2, subscription=subscription).put()
    user_pref3 = UserSubscriptionPreferences(preference=pref_3, subscription=subscription).put()
    meeting_spec1 = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.get().datetime)
    meeting_spec1.put()
    meeting_spec2 = MeetingSpec(meeting_subscription=subscription, datetime=pref_2.get().datetime)
    meeting_spec2.put()
    meeting_spec3 = MeetingSpec(meeting_subscription=subscription, datetime=pref_3.get().datetime)
    meeting_spec3.put()

    users = []
    num_users = 20
    for i in range(0, num_users):
        user = User(email='{}@yelp.com'.format(i), metadata={
                    'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref1, user_pref2, user_pref3])
        user.put()
        MeetingRequest(user=user.key, meeting_spec=meeting_spec1.key).put()
        MeetingRequest(user=user.key, meeting_spec=meeting_spec2.key).put()
        MeetingRequest(user=user.key, meeting_spec=meeting_spec3.key).put()
        users.append(user)

    meeting1 = Meeting(meeting_spec=meeting_spec1.key, cancelled=False).put()
    MeetingParticipant(meeting=meeting1, user=users[1].key).put()
    MeetingParticipant(meeting=meeting1, user=users[0].key).put()
    meeting2 = Meeting(meeting_spec=meeting_spec2.key, cancelled=False).put()
    MeetingParticipant(meeting=meeting2, user=users[1].key).put()
    MeetingParticipant(meeting=meeting2, user=users[0].key).put()
    meeting3 = Meeting(meeting_spec=meeting_spec3.key, cancelled=False).put()
    MeetingParticipant(meeting=meeting3, user=users[1].key).put()
    MeetingParticipant(meeting=meeting3, user=users[0].key).put()

    for run in range(10):
        matches, unmatched = generate_meetings(users, meeting_spec1, prev_meeting_tuples=None, group_size=3)
        assert(len(matches) == 6)
        assert (len(unmatched) == 2)
        for matched_group in matches:
            assert(not (users[0] in matched_group and users[1] in matched_group))
