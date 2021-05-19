from datetime import datetime

from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.routes.tasks import clean_user_subscriptions
from yelp_beans.routes.tasks import generate_meeting_specs
from yelp_beans.routes.tasks import weekly_opt_in


def test_generate_meeting_specs(database, session):
    # delete current specs
    MeetingSpec.query.delete()
    session.commit()
    meeting_specs = MeetingSpec.query.all()
    assert len(meeting_specs) == 0

    # ensure we create new specs
    generate_meeting_specs()
    meeting_specs = MeetingSpec.query.all()
    assert len(meeting_specs) == 2


def test_generate_meeting_specs_idempotent(database):
    # ensure we don't create more specs
    generate_meeting_specs()
    meeting_specs = MeetingSpec.query.all()
    assert len(meeting_specs) == 2


def test_weekly_opt_in(session, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription,
    )
    user1 = User(email="a@yelp.com", meta_data={'department': 'dept'}, subscription_preferences=[user_pref])

    session.add(preference)
    session.add(user_pref)
    session.add(user1)
    session.commit()

    response = weekly_opt_in()
    assert response == 'OK'


def test_clean_user_subscriptions(session):
    preference = SubscriptionDateTime(datetime=datetime(2017, 1, 20, 23, 0))
    subscription = MeetingSubscription(
        title='Test Weekly',
        size=2,
        location='8th Floor',
        office='USA: CA SF New Montgomery Office',
        timezone='America/Los_Angeles',
        datetime=[preference],
        user_rules=[Rule(name='department', value='dept')],
        rule_logic='all',
    )
    user_1 = User(
        email="a@yelp.com",
        meta_data={'department': 'dept'},
        subscription_preferences=[UserSubscriptionPreferences(preference=preference, subscription=subscription)],
    )
    # Should be removed because of incorrect department
    user_2 = User(
        email="a@yelp.com",
        meta_data={'department': 'other dept'},
        subscription_preferences=[UserSubscriptionPreferences(preference=preference, subscription=subscription)],
    )

    session.add(subscription)
    session.add(user_1)
    session.add(user_2)
    session.commit()

    response = clean_user_subscriptions()
    assert response == 'OK'

    user_sub_prefs = UserSubscriptionPreferences.query.all()
    assert len(user_sub_prefs) == 1
