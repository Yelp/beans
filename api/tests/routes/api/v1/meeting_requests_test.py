# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from yelp_beans.models import MeetingRequest
from yelp_beans.routes.api.v1 import meeting_requests
from yelp_beans.routes.api.v1.meeting_requests import create_delete_meeting_request
from yelp_beans.routes.api.v1.meeting_requests import get_meeting_request


def test_create_meeting_request(app, monkeypatch, database, fake_user):

    monkeypatch.setattr(meeting_requests, 'get_user', lambda(x): fake_user)

    meeting_spec_key = database.specs[0].key.urlsafe()
    with app.test_request_context(
        '/v1/meeting_request/',
        method='POST',
        data=json.dumps({
            'meeting_spec_key': meeting_spec_key,
            'meeting_request_key': '',
            'email': fake_user.email
        }),
        content_type='application/json'
    ):
        response = create_delete_meeting_request().json
        assert response['key'] != ''

    requests = MeetingRequest.query().fetch()
    assert len(requests) == 1
    assert requests[0].user == fake_user.key
    assert requests[0].meeting_spec == database.specs[0].key


def test_delete_meeting_request(app, monkeypatch, database, fake_user):

    monkeypatch.setattr(meeting_requests, 'get_user', lambda(x): fake_user)

    meeting_spec_key = database.specs[0].key.urlsafe()
    meeting_request = MeetingRequest(
        meeting_spec=database.specs[0].key,
        user=fake_user.key
    )
    meeting_request_key = meeting_request.put()
    meeting_request_key = meeting_request_key.urlsafe()
    requests = MeetingRequest.query().fetch()
    assert len(requests) == 1

    with app.test_request_context(
            '/v1/meeting_request/',
            method='POST',
            data=json.dumps({
                'meeting_spec_key': meeting_spec_key,
                'meeting_request_key': meeting_request_key,
                'email': fake_user.email
            }),
            content_type='application/json'
    ):
        response = create_delete_meeting_request().json
        assert response == {'key': ''}

    requests = MeetingRequest.query().fetch()
    assert len(requests) == 0


def test_get_meeting_request(app, monkeypatch, database, fake_user):
    monkeypatch.setattr(meeting_requests, 'get_user', lambda(x): fake_user)

    meeting_spec_key = database.specs[0].key.urlsafe()
    meeting_request = MeetingRequest(
        meeting_spec=database.specs[0].key,
        user=fake_user.key
    )
    meeting_request_key = meeting_request.put()
    requests = MeetingRequest.query().fetch()
    assert len(requests) == 1

    with app.test_request_context('/v1/meeting_request/' + meeting_spec_key):
        response = get_meeting_request(meeting_spec_key).json
        assert response == {'key': meeting_request_key.urlsafe()}


def test_get_meeting_request_no_exist(app, monkeypatch, database, fake_user):
    monkeypatch.setattr(meeting_requests, 'get_user', lambda(x): fake_user)

    meeting_spec_key = database.specs[0].key.urlsafe()
    requests = MeetingRequest.query().fetch()
    assert len(requests) == 0

    with app.test_request_context('/v1/meeting_request/' + meeting_spec_key):
        response = get_meeting_request(meeting_spec_key).json
        assert response == {'key': ''}
