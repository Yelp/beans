import itertools
from datetime import datetime
from datetime import timedelta

from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.matching.match import generate_meetings
from yelp_beans.matching.match_utils import get_meeting_weights
from yelp_beans.matching.pair_match import get_disallowed_meetings
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
    rule = Rule(name="department", value="")
    session.add(rule)
    subscription.dept_rules = [rule]
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(preference=preference, subscription=subscription)
    session.add(user_pref)
    user1 = User(
        id=1,
        email="a@yelp.com",
        meta_data={"department": "dept"},
        subscription_preferences=[user_pref],
        manager_id="0",
        languages="en, fr",
        days_since_start=100,
        employee_id="101",
        location="UK, London",
    )
    session.add(user1)
    user2 = User(
        id=2,
        email="b@yelp.com",
        meta_data={"department": "dept"},
        subscription_preferences=[user_pref],
        manager_id="101",
        languages="en, fr",
        days_since_start=100,
        employee_id="102",
        location="CA, London",
    )
    session.add(user2)
    user_list = [user1, user2]
    session.commit()

    _, specs = get_specs_from_subscription(subscription)
    matches, unmatched = generate_meetings(user_list, specs[0])
    assert len(unmatched) == 2
    assert len(matches) == 0


def test_generate_meetings_with_history(session, subscription):
    rule = Rule(name="department", value="")
    session.add(rule)
    subscription.dept_rules = [rule]

    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(preference=preference, subscription=subscription)
    session.add(user_pref)

    user1 = User(
        id=1,
        email="a@yelp.com",
        meta_data={"department": "dept"},
        subscription_preferences=[user_pref],
        manager_id="0",
        languages="en, fr",
        days_since_start=100,
        employee_id="101",
        location="UK, London",
    )
    session.add(user1)
    user2 = User(
        id=2,
        email="b@yelp.com",
        meta_data={"department": "dept2"},
        subscription_preferences=[user_pref],
        manager_id="101",
        languages="en, fr",
        days_since_start=100,
        employee_id="102",
        location="CA, London",
    )
    session.add(user2)
    user3 = User(
        id=3,
        email="c@yelp.com",
        meta_data={"department": "dept"},
        subscription_preferences=[user_pref],
        manager_id="101",
        languages="",
        days_since_start=100,
        employee_id="103",
        location="UK, London",
    )
    session.add(user3)
    user4 = User(
        id=4,
        email="d@yelp.com",
        meta_data={"department": "dept2"},
        subscription_preferences=[user_pref],
        manager_id="101",
        languages="en",
        days_since_start=100,
        employee_id="104",
        location="US, SF",
    )
    session.add(user4)

    user_list = [user1, user2, user3, user4]
    session.commit()
    week_start, specs = get_specs_from_subscription(subscription)
    store_specs_from_subscription(subscription, week_start, specs)

    matches, unmatched = generate_meetings(user_list, specs[0])
    assert len(matches) == 2
    assert len(unmatched) == 0

    meeting_history = set(
        [
            (user1.id, user2.id),
            (user3.id, user4.id),
            (user2.id, user3.id),
            (user1.id, user4.id),
        ]
    )
    matches, unmatched = generate_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 0
    assert len(unmatched) == 4

    meeting_history = set(
        [
            (user1.id, user2.id),
            (user3.id, user4.id),
            (user2.id, user3.id),
        ]
    )
    matches, unmatched = generate_meetings(user_list, specs[0], meeting_history)
    assert len(matches) == 1
    assert len(unmatched) == 2


def test_no_re_matches(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title="all engineering weekly", datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(meeting_spec)

    users = []
    num_users = 20
    for i in range(0, num_users):
        user = User(
            id=i,
            email=f"{i}@yelp.com",
            meta_data={"department": f"dept{i//2}"},
            subscription_preferences=[user_pref],
            manager_id="101",
            languages="en",
            days_since_start=100,
            employee_id=f"{100+i}",
            location="",
        )
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
    subscription = MeetingSubscription(title="all engineering weekly", datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(meeting_spec)

    users = []
    num_users = 21
    for i in range(0, num_users):
        user = User(email=f"{i}@yelp.com", meta_data={"department": f"dept{i}"}, subscription_preferences=[user_pref])
        session.add(user)
        mr = MeetingRequest(user=user, meeting_spec=meeting_spec)
        session.add(mr)
        users.append(user)

    session.commit()
    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=3)
    assert len(matches) == 7
    assert len(unmatched) == 0
    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=5)
    assert len(matches) == 4
    assert len(unmatched) == 1


def test_generate_group_meeting_invalid_number_of_users(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title="all engineering weekly", datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(meeting_spec)

    users = []
    for i in range(0, 2):
        user = User(email=f"{i}@yelp.com", meta_data={"department": f"dept{i}"}, subscription_preferences=[user_pref])
        session.add(user)
        mr = MeetingRequest(user=user, meeting_spec=meeting_spec)
        session.add(mr)
        users.append(user)

    session.commit()
    matches, unmatched = generate_meetings(users, meeting_spec, prev_meeting_tuples=None, group_size=3)
    assert len(matches) == 0
    assert len(unmatched) == 2


def test_previous_meeting_penalty(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    pref_2 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 2))
    pref_3 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 3))
    subscription = MeetingSubscription(title="all engineering weekly", datetime=[pref_1, pref_2, pref_3])
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
        user = User(
            email=f"{i}@yelp.com",
            meta_data={"department": f"dept{i}"},
            subscription_preferences=[user_pref1, user_pref2, user_pref3],
        )
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
        assert len(matches) == 6
        assert len(unmatched) == 2
        for matched_group in matches:
            assert not (users[0] in matched_group and users[1] in matched_group)


def test_pairwise_distance(session, subscription):
    rule = Rule(name="department", value="")
    session.add(rule)
    subscription.dept_rules = [rule]
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(preference=preference, subscription=subscription)
    session.add(user_pref)

    user0 = User(
        id=126,
        email="126@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="1073",
        languages="",
        days_since_start=317,
        employee_id="126",
        location="California, USA",
    )
    session.add(user0)

    user1 = User(
        id=223,
        email="223@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="782",
        languages="",
        days_since_start=115,
        employee_id="223",
        location="Berkshire, United Kingdom",
    )
    session.add(user1)

    user2 = User(
        id=707,
        email="707@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="782",
        languages="English, Farsi",
        days_since_start=509,
        employee_id="707",
        location="California, USA",
    )
    session.add(user2)

    user3 = User(
        id=782,
        email="782@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="2989",
        languages="",
        days_since_start=356,
        employee_id="782",
        location="California, USA",
    )
    session.add(user3)

    user4 = User(
        id=890,
        email="890@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="1073",
        languages="",
        days_since_start=54,
        employee_id="890",
        location="California, USA",
    )
    session.add(user4)

    user5 = User(
        id=1073,
        email="1073@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="2989",
        languages="Turkish",
        days_since_start=595,
        employee_id="1073",
        location="California, USA",
    )
    session.add(user5)

    user6 = User(
        id=1117,
        email="1117@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="782",
        languages="",
        days_since_start=338,
        employee_id="1117",
        location="Texas, USA",
    )
    session.add(user6)

    user7 = User(
        id=1460,
        email="1460@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5384",
        languages="",
        days_since_start=1265,
        employee_id="1460",
        location="California, USA",
    )
    session.add(user7)

    user8 = User(
        id=1463,
        email="1463@yelp.com",
        meta_data={"department": "Engineering - Growth"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=410,
        employee_id="1463",
        location="California, USA",
    )
    session.add(user8)

    user9 = User(
        id=1715,
        email="1715@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5384",
        languages="",
        days_since_start=269,
        employee_id="1715",
        location="New York, USA",
    )
    session.add(user9)

    user10 = User(
        id=2131,
        email="2131@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="782",
        languages="",
        days_since_start=880,
        employee_id="2131",
        location="Georgia, USA",
    )
    session.add(user10)

    user11 = User(
        id=2169,
        email="2169@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="782",
        languages="",
        days_since_start=309,
        employee_id="2169",
        location="California, USA",
    )
    session.add(user11)

    user12 = User(
        id=2241,
        email="2241@yelp.com",
        meta_data={"department": "Engineering - Engineering Effectiveness"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=98,
        employee_id="2241",
        location="British Columbia, Canada",
    )
    session.add(user12)

    user13 = User(
        id=2525,
        email="2525@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5384",
        languages="",
        days_since_start=492,
        employee_id="2525",
        location="New York, USA",
    )
    session.add(user13)

    user14 = User(
        id=2589,
        email="2589@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=511,
        employee_id="2589",
        location="Florida, USA",
    )
    session.add(user14)

    user15 = User(
        id=2989,
        email="2989@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=1202,
        employee_id="2989",
        location="California, USA",
    )
    session.add(user15)

    user16 = User(
        id=3002,
        email="3002@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5384",
        languages="",
        days_since_start=537,
        employee_id="3002",
        location="California, USA",
    )
    session.add(user16)

    user17 = User(
        id=3447,
        email="3447@yelp.com",
        meta_data={"department": "Engineering - Content Platform"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=692,
        employee_id="3447",
        location="Pennsylvania, USA",
    )
    session.add(user17)

    user18 = User(
        id=3457,
        email="3457@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="1073",
        languages="",
        days_since_start=542,
        employee_id="3457",
        location="Berlin, Germany",
    )
    session.add(user18)

    user19 = User(
        id=3601,
        email="3601@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5384",
        languages="",
        days_since_start=141,
        employee_id="3601",
        location="Ontario, Canada",
    )
    session.add(user19)

    user20 = User(
        id=3683,
        email="3683@yelp.com",
        meta_data={"department": "Engineering - Content Platform"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=428,
        employee_id="3683",
        location="California, USA",
    )
    session.add(user20)

    user21 = User(
        id=3815,
        email="3815@yelp.com",
        meta_data={"department": "Engineering - Engineering Effectiveness"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=1816,
        employee_id="3815",
        location="California, USA",
    )
    session.add(user21)

    user22 = User(
        id=3957,
        email="3957@yelp.com",
        meta_data={"department": "Engineering - Services Experience"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=86,
        employee_id="3957",
        location="British Columbia, Canada",
    )
    session.add(user22)

    user23 = User(
        id=4078,
        email="4078@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="782",
        languages="",
        days_since_start=266,
        employee_id="4078",
        location="New York, USA",
    )
    session.add(user23)

    user24 = User(
        id=4102,
        email="4102@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="5384",
        languages="",
        days_since_start=541,
        employee_id="4102",
        location="British Columbia, Canada",
    )
    session.add(user24)

    user25 = User(
        id=4292,
        email="4292@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="782",
        languages="English, Gujarati, Hindi",
        days_since_start=373,
        employee_id="4292",
        location="Washington, USA",
    )
    session.add(user25)

    user26 = User(
        id=4650,
        email="4650@yelp.com",
        meta_data={"department": "Engineering"},
        subscription_preferences=[user_pref],
        manager_id="2432",
        languages="",
        days_since_start=446,
        employee_id="4650",
        location="East Sussex, United Kingdom",
    )
    session.add(user26)

    user27 = User(
        id=5240,
        email="5240@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="2989",
        languages="",
        days_since_start=519,
        employee_id="5240",
        location="California, USA",
    )
    session.add(user27)

    user28 = User(
        id=5384,
        email="5384@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="2989",
        languages="",
        days_since_start=721,
        employee_id="5384",
        location="Quebec, Canada",
    )
    session.add(user28)

    user29 = User(
        id=5529,
        email="5529@yelp.com",
        meta_data={"department": "Engineering - Services Leads"},
        subscription_preferences=[user_pref],
        manager_id="5543",
        languages="",
        days_since_start=240,
        employee_id="5529",
        location="California, USA",
    )
    session.add(user29)

    user30 = User(
        id=5543,
        email="5543@yelp.com",
        meta_data={"department": "Engineering"},
        subscription_preferences=[user_pref],
        manager_id="4650",
        languages="",
        days_since_start=610,
        employee_id="5543",
        location="California, USA",
    )
    session.add(user30)

    user31 = User(
        id=5637,
        email="5637@yelp.com",
        meta_data={"department": "Engineering - Core Experience"},
        subscription_preferences=[user_pref],
        manager_id="1073",
        languages="",
        days_since_start=226,
        employee_id="5637",
        location="California, USA",
    )
    session.add(user31)

    user_list = [
        user0,
        user1,
        user2,
        user3,
        user4,
        user5,
        user6,
        user7,
        user8,
        user9,
        user10,
        user11,
        user12,
        user13,
        user14,
        user15,
        user16,
        user17,
        user18,
        user19,
        user20,
        user21,
        user22,
        user23,
        user24,
        user25,
        user26,
        user27,
        user28,
        user29,
        user30,
        user31,
    ]
    user_ids = [user.id for user in user_list]
    session.commit()

    # considering disallowed meetings and rules
    meeting_history = set(
        [
            (user1.id, user2.id),
            (user3.id, user4.id),
            (user2.id, user3.id),
        ]
    )

    _, specs = get_specs_from_subscription(subscription)
    possible_meetings = {tuple(sorted(meeting)) for meeting in itertools.combinations(user_ids, 2)}
    disallowed_meetings = get_disallowed_meetings(user_list, meeting_history, specs[0])
    allowed_meetings = possible_meetings - {tuple(sorted(a)) for a in disallowed_meetings}
    paired_distance = get_meeting_weights(allowed_meetings)

    assert (126, 223) not in paired_distance.keys()  # historically paired not in paired_distance bc historical
    assert (2169, 5384) not in paired_distance.keys()  # same department members should not be paired
    assert round(paired_distance[(3457, 3815)], 3) == 2.102
    assert round(paired_distance[(4102, 4650)], 3) == 1.452
