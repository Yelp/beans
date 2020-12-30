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


def test_generate_meetings_same_department(session, subscription):
    rule = Rule(name='department', value='')
    session.add(rule)
    subscription.dept_rules = [rule]
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(preference=preference, subscription=subscription)
    session.add(user_pref)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    session.add(user1)
    user2 = User(email='b@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    session.add(user2)
    user_list = [user1, user2]
    session.commit()

    _, specs = get_specs_from_subscription(subscription)
    matches, unmatched = generate_meetings(user_list, specs[0])
    assert len(unmatched) == 2
    assert len(matches) == 0


def test_generate_meetings_with_history(session, subscription):
    rule = Rule(name='department', value='')
    session.add(rule)
    subscription.dept_rules = [rule]

    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(preference=preference, subscription=subscription)
    session.add(user_pref)

    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    session.add(user1)
    user2 = User(email='b@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    session.add(user2)
    user3 = User(email='c@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    session.add(user3)
    user4 = User(email='d@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    session.add(user4)

    user_list = [user1, user2, user3, user4]
    session.commit()
    week_start, specs = get_specs_from_subscription(subscription)
    store_specs_from_subscription(subscription, week_start, specs)

    matches, unmatched = generate_meetings(user_list, specs[0])
    assert len(matches) == 2
    assert len(unmatched) == 0

    meeting_history = set([
        (user1.id, user2.id),
        (user3.id, user4.id),
        (user2.id, user3.id),
        (user1.id, user4.id),
    ])
    matches, unmatched = generate_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 0
    assert len(unmatched) == 4

    meeting_history = set([
        (user1.id, user2.id),
        (user3.id, user4.id),
        (user2.id, user3.id),
    ])
    matches, unmatched = generate_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 1
    assert len(unmatched) == 2


def test_no_re_matches(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(meeting_spec)

    users = []
    num_users = 20
    for i in range(0, num_users):
        user = User(email='{}@yelp.com'.format(i), meta_data={
                    'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref])
        session.add(user)
        mr = MeetingRequest(user=user, meeting_spec=meeting_spec)
        session.add(mr)
        users.append(user)
    session.commit()

    previous_meetings = {pair for pair in itertools.combinations([user.id for user in users], 2)}
    previous_meetings = previous_meetings - {(users[0].id, users[1].id)}
    matches, unmatched = generate_meetings(users, meeting_spec, previous_meetings)
    assert len(unmatched) == num_users - 2
    assert [(match[0].id, match[1].id) for match in matches] == [(users[0].id, users[1].id)]


def test_generate_group_meeting(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(meeting_spec)

    users = []
    num_users = 21
    for i in range(0, num_users):
        user = User(email='{}@yelp.com'.format(i), meta_data={
                    'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref])
        session.add(user)
        mr = MeetingRequest(user=user, meeting_spec=meeting_spec)
        session.add(mr)
        users.append(user)

    session.commit()
    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=3)
    assert(len(matches) == 7)
    assert (len(unmatched) == 0)
    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=5)
    assert(len(matches) == 4)
    assert (len(unmatched) == 1)


def test_generate_group_meeting_invalid_number_of_users(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(meeting_spec)

    users = []
    for i in range(0, 2):
        user = User(email='{}@yelp.com'.format(i), meta_data={
            'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref])
        session.add(user)
        mr = MeetingRequest(user=user, meeting_spec=meeting_spec)
        session.add(mr)
        users.append(user)

    session.commit()
    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=3)
    assert(len(matches) == 0)
    assert (len(unmatched) == 2)


def test_previous_meeting_penalty(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    pref_2 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 2))
    pref_3 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 3))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1, pref_2, pref_3])
    user_pref1 = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user_pref2 = UserSubscriptionPreferences(preference=pref_2, subscription=subscription)
    user_pref3 = UserSubscriptionPreferences(preference=pref_3, subscription=subscription)
    meeting_spec1 = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    meeting_spec2 = MeetingSpec(meeting_subscription=subscription, datetime=pref_2.datetime)
    meeting_spec3 = MeetingSpec(meeting_subscription=subscription, datetime=pref_3.datetime)
    session.add(pref_1)
    session.add(pref_2)
    session.add(pref_3)
    session.add(subscription)
    session.add(user_pref1)
    session.add(user_pref2)
    session.add(user_pref3)
    session.add(meeting_spec1)
    session.add(meeting_spec2)
    session.add(meeting_spec3)

    users = []
    num_users = 20
    for i in range(0, num_users):
        user = User(email='{}@yelp.com'.format(i), meta_data={
                    'department': 'dept{}'.format(i)}, subscription_preferences=[user_pref1, user_pref2, user_pref3])
        session.add(user)
        mr1 = MeetingRequest(user=user, meeting_spec=meeting_spec1)
        mr2 = MeetingRequest(user=user, meeting_spec=meeting_spec2)
        mr3 = MeetingRequest(user=user, meeting_spec=meeting_spec3)
        session.add(mr1)
        session.add(mr2)
        session.add(mr3)
        users.append(user)

    meeting1 = Meeting(meeting_spec=meeting_spec1, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting1, user=users[1])
    mp2 = MeetingParticipant(meeting=meeting1, user=users[0])
    session.add(meeting1)
    session.add(mp1)
    session.add(mp2)

    meeting2 = Meeting(meeting_spec=meeting_spec2, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting2, user=users[1])
    mp2 = MeetingParticipant(meeting=meeting2, user=users[0])
    session.add(meeting2)
    session.add(mp1)
    session.add(mp2)

    meeting3 = Meeting(meeting_spec=meeting_spec3, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting3, user=users[1])
    mp2 = MeetingParticipant(meeting=meeting3, user=users[0])
    session.add(meeting3)
    session.add(mp1)
    session.add(mp2)

    session.commit()

    for run in range(10):
        matches, unmatched = generate_meetings(users, meeting_spec1, prev_meeting_tuples=None, group_size=3)
        assert(len(matches) == 6)
        assert (len(unmatched) == 2)
        for matched_group in matches:
            assert(not (users[0] in matched_group and users[1] in matched_group))
