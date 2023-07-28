import datetime
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest
import pytz
from yelp_beans.logic.meeting_spec import get_specs_for_current_week
from yelp_beans.matching.match import generate_meetings
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences
from yelp_beans.send_email import create_google_calendar_invitation_link
from yelp_beans.send_email import send_batch_initial_opt_in_email
from yelp_beans.send_email import send_batch_meeting_confirmation_email
from yelp_beans.send_email import send_batch_unmatched_email
from yelp_beans.send_email import send_batch_weekly_opt_in_email


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_weekly_opt_in_email(database, fake_user):
    for spec in get_specs_for_current_week():
        send_batch_weekly_opt_in_email(spec)


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_initial_opt_in_email(database, fake_user):
    send_batch_initial_opt_in_email([fake_user])


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_meeting_confirmation_email(database, session):
    pref = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    s3_url = "https://s3-media2.fl.yelpcdn.com/assets/srv0/yelp_large_assets/"
    user_a = User(
        email="rkwills@yelp.com",
        photo_url=s3_url + "a315bcce34b3/assets/img/illustrations/mascots/hammy.png",
        first_name="Hammy",
        last_name="Yelp",
        meta_data={"department": "Engineering"},
        subscription_preferences=[pref],
    )
    user_b = User(
        first_name="Darwin",
        last_name="Yelp",
        email="darwin@yelp.com",
        photo_url=s3_url + "36a31704362e/assets/img/illustrations/mascots/darwin.png",
        meta_data={"department": "Design"},
        subscription_preferences=[pref],
    )
    user_c = User(
        first_name="Carmin",
        last_name="Yelp",
        email="darwin@yelp.com",
        photo_url=s3_url + "d71947670be7/assets/img/illustrations/mascots/carmen.png",
        meta_data={"department": "Design"},
        subscription_preferences=[pref],
    )
    session.add(pref)
    session.add(user_a)
    session.add(user_b)
    session.add(user_c)
    session.commit()

    matches = [tuple((user_a, user_b, user_c, pref))]
    send_batch_meeting_confirmation_email(matches, database.specs[0])


@pytest.mark.skip(reason="Testing Emails should be run locally with client_secrets.json present")
def test_send_batch_unmatched_email(database, fake_user):
    matches, unmatched = generate_meetings([fake_user], database.specs[0])
    send_batch_unmatched_email(unmatched)


@pytest.mark.parametrize(
    "test_datetime,expected_link_ctz",
    [
        (datetime.datetime(2022, 5, 13, 23, 34, 45, tzinfo=pytz.timezone("America/Chicago")), "America/Chicago"),
        (datetime.datetime(2022, 5, 13, 23, 34, 45, tzinfo=pytz.timezone("America/Los_Angeles")), "America/Los_Angeles"),
        (datetime.datetime(2022, 5, 13, 23, 34, 45, tzinfo=pytz.timezone("Europe/London")), "Europe/London"),
        (datetime.datetime(2022, 5, 13, 23, 34, 45), None),
    ],
)
def test_create_google_calendar_invitation_link(test_datetime, expected_link_ctz):
    generated_calendar_url = create_google_calendar_invitation_link(
        [], "title", "office", "location", test_datetime, test_datetime
    )
    parsed_url = urlparse(generated_calendar_url)
    ctz_param = parse_qs(parsed_url.query).get("ctz", None)
    ctz_value = ctz_param[0] if ctz_param else None
    assert ctz_value == expected_link_ctz
