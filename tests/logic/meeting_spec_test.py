# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.meeting_spec import get_users_from_spec


def test_get_users_from_spec(database, fake_user):
    users = get_users_from_spec(database.specs[0])
    assert len(users) == 1


def test_get_meeting_datetime(database, subscription):
    assert get_meeting_datetime(database.specs[0]).hour == 15


def test_get_meeting_datetime_user_timezone(database, fake_user):
    fake_user.timezone = 'America/Edmonton'
    meeting_time = get_meeting_datetime(database.specs[0], fake_user)

    assert meeting_time.tzinfo.zone == fake_user.timezone, (
        "The meeting time should be in the user's timezone"
    )


def test_get_meeting_datetime_user_no_timezone(database, fake_user):
    fake_user.timezone = None
    localtime = get_meeting_datetime(database.specs[0], fake_user)

    meeting_spec_timezone = database.specs[0].meeting_subscription.get().timezone
    assert localtime.tzinfo.zone == meeting_spec_timezone, (
        'User has no timezone, the meeting timezone should default to the meeting spec'
    )
