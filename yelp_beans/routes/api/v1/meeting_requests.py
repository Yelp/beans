# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
from google.appengine.ext import ndb

from flask import Blueprint
from flask import request

from yelp_beans.logic.user import get_user
from yelp_beans.models import MeetingRequest


meeting_requests = Blueprint(
    'meeting_requests', __name__, template_folder='templates')


def query_meeting_request(meeting_spec, user):
    return MeetingRequest().query(
        MeetingRequest.meeting_spec == meeting_spec,
        MeetingRequest.user == user.key
    ).get()


@meeting_requests.route('/', methods=['POST'])
def create_delete_meeting_request():
    user = get_user()
    data = request.json
    meeting_spec_key = data['meeting_spec_key']
    meeting_request_key = data['meeting_request_key']

    if meeting_request_key == '':
        meeting_spec = ndb.Key(urlsafe=meeting_spec_key)
        if not meeting_spec:
            return 400
        meeting_request = query_meeting_request(meeting_spec, user)

        if not meeting_request:
            meeting_request = MeetingRequest(meeting_spec=meeting_spec, user=user.key)
            meeting_request.put()

        return json.dumps({'key': meeting_request.key.urlsafe()})
    else:
        meeting_request = ndb.Key(urlsafe=meeting_request_key)
        meeting_request.delete()
        return json.dumps({'key': ''})


@meeting_requests.route('/<meeting_spec_key>', methods=['GET'])
def get_meeting_request(meeting_spec_key):
    user = get_user()
    meeting_spec = ndb.Key(urlsafe=meeting_spec_key)
    meeting_request = query_meeting_request(meeting_spec, user)

    return json.dumps({'key': meeting_request.key.urlsafe() if meeting_request else ""})
