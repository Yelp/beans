from yelp_beans.logic.meeting_request import query_meeting_request
from yelp_beans.logic.meeting_request import store_meeting_request
from yelp_beans.models import MeetingRequest
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def test_store_meeting_request(database, session):
    pref = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    user = User(email="a@yelp.com", meta_data={"department": "dept"}, subscription_preferences=[pref])
    mr = MeetingRequest(user=user, meeting_spec=database.specs[0])
    database.specs[0]

    session.add(pref)
    session.add(user)
    session.add(mr)
    session.commit()

    stored_meeting_id = store_meeting_request(mr)

    assert stored_meeting_id == mr.id


def test_query_meeting_request(database, session):
    pref = UserSubscriptionPreferences(subscription=database.sub, preference=database.prefs[0])
    user = User(email="a@yelp.com", meta_data={"department": "dept"}, subscription_preferences=[pref])
    mr = MeetingRequest(user=user, meeting_spec=database.specs[0])
    spec = database.specs[0]

    session.add(pref)
    session.add(user)
    session.add(mr)
    session.commit()

    result = query_meeting_request(spec, user)

    assert result == mr
