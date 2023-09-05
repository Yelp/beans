from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.meeting_spec import get_users_from_spec


def test_get_users_from_spec(database, fake_user):
    users = get_users_from_spec(database.specs[0])
    assert len(users) == 1


def test_get_users_from_spec_excluding_users_with_auto_opt_in_enabled(database, fake_user):
    users = get_users_from_spec(database.specs[0], exclude_user_prefs_with_auto_opt_in=True)
    assert len(users) == 0


def test_get_meeting_datetime(database, subscription):
    assert get_meeting_datetime(database.specs[0]).hour == 15
