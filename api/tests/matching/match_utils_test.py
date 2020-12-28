# -*- coding: utf-8 -*-
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


def test_generate_save_meetings(session, subscription):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='b@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    mr1 = MeetingRequest(user=user1, meeting_spec=meeting_spec)
    mr2 = MeetingRequest(user=user2, meeting_spec=meeting_spec)

    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(user1)
    session.add(user2)
    session.add(meeting_spec)
    session.add(mr1)
    session.add(mr2)
    session.commit()

    matches, unmatched = generate_meetings([user1, user2], meeting_spec)
    save_meetings(matches, meeting_spec)

    assert unmatched == []

    participants = [
        participant.user
        for participant in MeetingParticipant.query.all()
    ]

    assert participants == [user1, user2]


def test_get_previous_meetings(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='a@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
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

    assert get_previous_meetings(subscription) == set([(user1.id, user2.id)])


def test_get_previous_meetings_multi_subscription(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription1 = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    subscription2 = MeetingSubscription(title='all sales weekly', datetime=[pref_1])
    user_pref1 = UserSubscriptionPreferences(preference=pref_1, subscription=subscription1)
    user_pref2 = UserSubscriptionPreferences(preference=pref_1, subscription=subscription2)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref1, user_pref2])
    user2 = User(email='a@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref1, user_pref2])
    meeting_spec1 = MeetingSpec(meeting_subscription=subscription1, datetime=pref_1.datetime)
    meeting = Meeting(meeting_spec=meeting_spec1, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting, user=user2)
    mp2 = MeetingParticipant(meeting=meeting, user=user1)

    session.add(pref_1)
    session.add(subscription1)
    session.add(subscription2)
    session.add(user_pref1)
    session.add(user_pref2)
    session.add(user1)
    session.add(user2)
    session.add(meeting_spec1)
    session.add(meeting)
    session.add(mp1)
    session.add(mp2)
    session.commit()

    assert get_previous_meetings(subscription1) == set([(user1.id, user2.id)])
    assert get_previous_meetings(subscription2) == set([])


def test_get_previous_multi_meetings(session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS - 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='a@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=pref_1.datetime)
    meeting1 = Meeting(meeting_spec=meeting_spec, cancelled=False)
    meeting2 = Meeting(meeting_spec=meeting_spec, cancelled=False)
    mp1 = MeetingParticipant(meeting=meeting1, user=user2)
    mp2 = MeetingParticipant(meeting=meeting1, user=user1)
    mp3 = MeetingParticipant(meeting=meeting2, user=user2)
    mp4 = MeetingParticipant(meeting=meeting2, user=user1)

    session.add(pref_1)
    session.add(subscription)
    session.add(user_pref)
    session.add(user1)
    session.add(user2)
    session.add(meeting_spec)
    session.add(meeting1)
    session.add(meeting2)
    session.add(mp1)
    session.add(mp2)
    session.add(mp3)
    session.add(mp4)
    session.commit()

    assert get_previous_meetings(subscription) == set([(user1.id, user2.id), (user1.id, user2.id)])


def test_get_previous_meetings_no_specs(database_no_specs, session):
    pref_1 = SubscriptionDateTime(datetime=datetime.now() - timedelta(weeks=MEETING_COOLDOWN_WEEKS + 1))
    subscription = MeetingSubscription(title='all engineering weekly', datetime=[pref_1])
    user_pref = UserSubscriptionPreferences(preference=pref_1, subscription=subscription)
    user1 = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    user2 = User(email='a@yelp.com', meta_data={'department': 'dept2'}, subscription_preferences=[user_pref])
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

    assert get_previous_meetings(subscription) == set([])
