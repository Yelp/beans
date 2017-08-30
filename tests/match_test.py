# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import itertools
from datetime import datetime
from datetime import timedelta

from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.matching.group_match import generate_groups
from yelp_beans.matching.group_match import get_previous_meetings_counts
from yelp_beans.matching.group_match import get_user_weights
from yelp_beans.matching.match import generate_meetings
from yelp_beans.matching.match_utils import get_counts_for_pairs
from yelp_beans.matching.match_utils import get_previous_meetings
from yelp_beans.matching.match_utils import save_meetings
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


def test_pair_to_counts():
    pairs = [('user1', 'user2'), ('user1', 'user2'), ('user2', 'user3')]
    counts = get_counts_for_pairs(pairs)
    assert (counts[('user2', 'user3')] == 1)
    assert(counts[('user1', 'user2')] == 2)


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


def test_generate_groups():
    result = generate_groups([1, 2, 3, 4, 5], 3)
    assert [x for x in result] == [[1, 2, 3], [4, 5]]

    result = generate_groups([1, 2, 3, 4], 2)
    assert [x for x in result] == [[1, 2], [3, 4]]

    result = generate_groups([1, 2, 3], 3)
    assert [x for x in result] == [[1, 2, 3]]


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
