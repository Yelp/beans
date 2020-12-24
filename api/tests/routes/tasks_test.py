# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.models import MeetingSpec
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
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
