import logging
import time
from collections import namedtuple
from datetime import datetime
from pathlib import Path
from unittest import mock

import pytest
from database import db
from factory import create_app
from pytz import timezone
from pytz import utc
from yelp_beans import send_email
from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences

FAKE_USER = [
    {
        "first_name": "Darwin",
        "last_name": "Yelp",
        "email": "darwin@yelp.com",
        "photo_url": (
            "https://s3-media4.fl.yelpcdn.com/assets/"
            "srv0/yelp_large_assets/3f74899c069c"
            "/assets/img/illustrations/mascots/darwin@2x.png"
        ),
        "department": "Consumer",
        "business_title": "Engineer",
    }
]


@pytest.fixture(scope="session", autouse=True)
def mock_config():
    config = Path(__file__).parent / "test_data/config.yaml"
    with config.open() as config_file:
        data = config_file.read()
    with mock.patch("yelp_beans.logic.config.open", mock.mock_open(read_data=data)):
        yield


@pytest.fixture(scope="session", autouse=True)
def sendgrid_mock():
    """This is active to prevent from sending a emails when testing"""
    with mock.patch.object(send_email, "send_single_email"):
        yield


@pytest.fixture()
def app():
    """Session-wide test `Flask` application writing to test database."""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def session(app):
    """Creates a new database session for a test."""
    with app.app_context():
        yield db.session


@pytest.fixture
def subscription(session):
    yield _subscription(session)


def _subscription(session):
    zone = "America/Los_Angeles"
    preference_1 = SubscriptionDateTime(datetime=datetime(2017, 1, 20, 23, 0, tzinfo=utc))
    # Easier to think/verify in Pacific time since we are based in SF
    assert preference_1.datetime.astimezone(timezone(zone)).hour == 15
    preference_1.datetime = preference_1.datetime.replace(tzinfo=None)
    session.add(preference_1)

    preference_2 = SubscriptionDateTime(datetime=datetime(2017, 1, 20, 19, 0, tzinfo=utc))
    # Easier to think/verify in Pacific time since we are based in SF
    assert preference_2.datetime.astimezone(timezone(zone)).hour == 11
    preference_2.datetime = preference_2.datetime.replace(tzinfo=None)
    session.add(preference_2)

    rule = Rule(name="office", value="USA: CA SF New Montgomery Office")
    session.add(rule)

    subscription = MeetingSubscription(
        title="Yelp Weekly",
        size=2,
        location="8th Floor",
        office="USA: CA SF New Montgomery Office",
        timezone=zone,
        datetime=[preference_1, preference_2],
        user_rules=[rule],
    )
    session.add(subscription)
    session.commit()
    return subscription


@pytest.fixture
def database(session, subscription):
    MeetingInfo = namedtuple("MeetingInfo", ["sub", "specs", "prefs"])
    week_start, specs = get_specs_from_subscription(subscription)
    store_specs_from_subscription(subscription, week_start, specs)
    return MeetingInfo(subscription, specs, [subscription.datetime[0], subscription.datetime[1]])


@pytest.fixture
def database_no_specs(session, subscription):
    MeetingInfo = namedtuple("MeetingInfo", ["sub", "specs", "prefs"])
    return MeetingInfo(subscription, [], [subscription.datetime[0], subscription.datetime[1]])


@pytest.fixture
def employees():
    with open("tests/test_data/employees.json") as test_file:
        return test_file.read()


@pytest.fixture
def data_source():
    yield [
        {
            "first_name": "Sam",
            "last_name": "Smith",
            "email": "samsmith@yelp.com",
            "photo_url": "www.cdn.com/SamSmith.png",
            "metadata": {"department": "Engineering", "title": "Engineer", "floor": "10", "desk": "100", "manager": "Bo Demillo"},
        },
        {
            "first_name": "Derrick",
            "last_name": "Johnson",
            "email": "derrickjohnson@yelp.com",
            "photo_url": "www.cdn.com/DerrickJohnson.png",
            "metadata": {"department": "Design", "title": "Designer", "floor": "12", "desk": "102", "manager": "Tracy Borne"},
        },
    ]


@pytest.fixture
def data_source_by_key():
    yield {
        "samsmith@yelp.com": {
            "first_name": "Sam",
            "last_name": "Smith",
            "email": "samsmith@yelp.com",
            "photo_url": "www.cdn.com/SamSmith.png",
            "metadata": {"department": "Engineering", "title": "Engineer", "floor": "10", "desk": "100", "manager": "Bo Demillo"},
        },
        "derrickjohnson@yelp.com": {
            "first_name": "Derrick",
            "last_name": "Johnson",
            "email": "derrickjohnson@yelp.com",
            "photo_url": "www.cdn.com/DerrickJohnson.png",
            "metadata": {"department": "Design", "title": "Designer", "floor": "12", "desk": "102", "manager": "Derrick Johnson"},
        },
    }


@pytest.fixture
def fake_user(session):
    yield _fake_user(session)


def _fake_user(session):
    user_list = []
    subscription = MeetingSubscription.query.first()
    for user in FAKE_USER:
        preferences = UserSubscriptionPreferences(
            preference=subscription.datetime[0],
            subscription=subscription,
        )
        session.add(preferences)
        user_entity = User(
            first_name=user["first_name"],
            last_name=user["last_name"],
            email=user["email"],
            photo_url=user["photo_url"],
            meta_data={
                "department": user["department"],
                "office": "USA: CA SF New Montgomery Office",
                "company_profile_url": "https://www.yelp.com/user_details?userid=nkN_do3fJ9xekchVC-v68A",
            },
            subscription_preferences=[preferences],
        )
        session.add(user_entity)
        user_list.append(user_entity)
    session.commit()
    return user_list[0]


def create_dev_data(session):
    email = FAKE_USER[0]["email"]
    user = User.query.filter(User.email == email).first()
    if not user:
        _subscription(session)
        time.sleep(2)
        _fake_user(session)

        subscription = MeetingSubscription.query.first()
        week_start, specs = get_specs_from_subscription(subscription)
        store_specs_from_subscription(subscription, week_start, specs)
        logging.info("generated fake date for dev")
