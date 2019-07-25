# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from flask import Blueprint
from flask import jsonify
from flask import request
from google.appengine.ext import ndb
from yelp_beans.logic.user import get_user
from yelp_beans.models import MeetingRequest


meeting_requests = Blueprint('meeting_requests', __name__, template_folder='templates')


def query_meeting_request(meeting_spec, user):
    return MeetingRequest().query(
        MeetingRequest.meeting_spec == meeting_spec,
        MeetingRequest.user == user.key
    ).get()


@meeting_requests.route('/', methods=['POST'])
def create_delete_meeting_request():
    data = request.json
    meeting_spec_key = data['meeting_spec_key']
    meeting_request_key = data['meeting_request_key']
    user = get_user(data['email'])

    if meeting_request_key == '':
        meeting_spec = ndb.Key(urlsafe=meeting_spec_key)
        if not meeting_spec:
            return 400
        meeting_request = query_meeting_request(meeting_spec, user)

        if not meeting_request:
            meeting_request = MeetingRequest(meeting_spec=meeting_spec, user=user.key)
            meeting_request.put()

        return jsonify({'key': meeting_request.key.urlsafe()})
    else:
        meeting_request = ndb.Key(urlsafe=meeting_request_key)
        meeting_request.delete()
        return jsonify({'key': ''})


@meeting_requests.route('/<meeting_spec_key>', methods=['GET'])
def get_meeting_request(meeting_spec_key):
    user = get_user(request.args.get('email'))
    meeting_spec = ndb.Key(urlsafe=meeting_spec_key)
    meeting_request = query_meeting_request(meeting_spec, user)

    resp = jsonify({'key': meeting_request.key.urlsafe() if meeting_request else ""})
    resp.status_code = 200
    return resp
