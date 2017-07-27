# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import itertools
from datetime import datetime
from datetime import timedelta

from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.matching.pair_match import generate_pair_meetings
from yelp_beans.matching.pair_match import get_previous_pair_meetings
from yelp_beans.matching.pair_match import save_pair_meetings
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
    matches, unmatched = generate_pair_meetings(user_list, specs[0])
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

    matches, unmatched = generate_pair_meetings(user_list, specs[0])
    assert len(matches) == 2
    assert len(unmatched) == 0

    meeting_history = set([
        (user1.key.id(), user2.key.id()),
        (user3.key.id(), user4.key.id()),
        (user2.key.id(), user3.key.id()),
        (user1.key.id(), user4.key.id()),
    ])
    matches, unmatched = generate_pair_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 0
    assert len(unmatched) == 4

    meeting_history = set([
        (user1.key.id(), user2.key.id()),
        (user3.key.id(), user4.key.id()),
        (user2.key.id(), user3.key.id()),
    ])
    matches, unmatched = generate_pair_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 1
    assert len(unmatched) == 2


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

    assert get_previous_pair_meetings() == set([(user1.id(), user2.id())])


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

    assert get_previous_pair_meetings() == set([])


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

    matches, unmatched = generate_pair_meetings([user1.get(), user2.get()], meeting_spec)
    save_pair_meetings(matches, meeting_spec)

    assert unmatched == []

    participants = [
        participant.user
        for participant in MeetingParticipant.query().fetch()
    ]

    assert participants == [user1, user2]


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
    matches, unmatched = generate_pair_meetings(users, meeting_spec, previous_meetings)
    assert len(unmatched) == num_users - 2
    assert [(match[0].key.id(), match[1].key.id()) for match in matches] == [(users[0].key.id(), users[1].key.id())]
