import json

from yelp_beans.models import MeetingRequest
from yelp_beans.routes.api.v1 import meeting_requests
from yelp_beans.routes.api.v1.meeting_requests import create_delete_meeting_request
from yelp_beans.routes.api.v1.meeting_requests import get_meeting_request


def test_create_meeting_request(app, monkeypatch, database, fake_user):
    monkeypatch.setattr(meeting_requests, "get_user", lambda x: fake_user)

    meeting_spec_key = database.specs[0].id
    with app.test_request_context(
        "/v1/meeting_request/",
        method="POST",
        data=json.dumps({"meeting_spec_key": meeting_spec_key, "meeting_request_key": "", "email": fake_user.email}),
        content_type="application/json",
    ):
        response = create_delete_meeting_request().json
        assert response["key"] != ""

    requests = MeetingRequest.query.all()
    assert len(requests) == 1
    assert requests[0].user == fake_user
    assert requests[0].meeting_spec == database.specs[0]


def test_delete_meeting_request(app, monkeypatch, database, fake_user, session):
    monkeypatch.setattr(meeting_requests, "get_user", lambda x: fake_user)

    meeting_spec_key = database.specs[0].id
    meeting_request = MeetingRequest(meeting_spec=database.specs[0], user=fake_user)
    session.add(meeting_request)
    session.commit()

    meeting_request_key = meeting_request.id
    requests = MeetingRequest.query.all()
    assert len(requests) == 1

    with app.test_request_context(
        "/v1/meeting_request/",
        method="POST",
        data=json.dumps(
            {"meeting_spec_key": meeting_spec_key, "meeting_request_key": meeting_request_key, "email": fake_user.email}
        ),
        content_type="application/json",
    ):
        response = create_delete_meeting_request().json
        assert response == {"key": ""}

    requests = MeetingRequest.query.all()
    assert len(requests) == 0


def test_get_meeting_request(app, monkeypatch, database, fake_user, session):
    monkeypatch.setattr(meeting_requests, "get_user", lambda x: fake_user)

    meeting_spec_key = database.specs[0].id
    meeting_request = MeetingRequest(meeting_spec=database.specs[0], user=fake_user)
    session.add(meeting_request)
    session.commit()

    meeting_request_key = meeting_request.id
    requests = MeetingRequest.query.all()
    assert len(requests) == 1

    with app.test_request_context(f"/v1/meeting_request/{meeting_spec_key}"):
        response = get_meeting_request(meeting_spec_key).json
        assert response == {"key": meeting_request_key}


def test_get_meeting_request_no_exist(app, monkeypatch, database, fake_user):
    monkeypatch.setattr(meeting_requests, "get_user", lambda x: fake_user)

    meeting_spec_key = database.specs[0].id
    requests = MeetingRequest.query.all()
    assert len(requests) == 0

    with app.test_request_context(f"/v1/meeting_request/{meeting_spec_key}"):
        response = get_meeting_request(meeting_spec_key).json
        assert response == {"key": ""}
