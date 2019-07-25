# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from google.appengine.ext import ndb
from yelp_beans.models import MeetingSpec
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.routes.tasks import generate_meeting_specs
from yelp_beans.routes.tasks import weekly_opt_in


def test_generate_meeting_specs(database):
    # delete current specs
    keys = [key for key in MeetingSpec.query().iter(keys_only=True)]
    ndb.delete_multi(keys)
    meeting_specs = MeetingSpec.query().fetch()
    assert len(meeting_specs) == 0

    # ensure we create new specs
    generate_meeting_specs()
    meeting_specs = MeetingSpec.query().fetch()
    assert len(meeting_specs) == 2


def test_generate_meeting_specs_idempotent(database):
    # ensure we don't create more specs
    generate_meeting_specs()
    meeting_specs = MeetingSpec.query().fetch()
    assert len(meeting_specs) == 2


def test_weekly_opt_in(minimal_database, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription.key,
    ).put()
    user1 = User(email="a@yelp.com", metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user1.put()
    response = weekly_opt_in()
    assert response == 'OK'
