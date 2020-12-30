from database import db
from flask import Blueprint
from flask import jsonify
from flask import request
from yelp_beans.logic.user import get_user
from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSpec


meeting_requests = Blueprint('meeting_requests', __name__, template_folder='templates')


def query_meeting_request(meeting_spec, user):
    return MeetingRequest.query.filter(
        MeetingRequest.meeting_spec_id == meeting_spec.id,
        MeetingRequest.user_id == user.id
    ).first()


@meeting_requests.route('/', methods=['POST'])
def create_delete_meeting_request():
    data = request.json
    meeting_spec_key = data['meeting_spec_key']
    meeting_request_key = data['meeting_request_key']
    user = get_user(data['email'])

    if meeting_request_key == '':
        meeting_spec = MeetingSpec.query.filter(
            MeetingSpec.id == meeting_spec_key).first()
        if not meeting_spec:
            return 400
        meeting_request = query_meeting_request(meeting_spec, user)

        if not meeting_request:
            meeting_request = MeetingRequest(meeting_spec=meeting_spec, user=user)
            db.session.add(meeting_request)
            db.session.commit()

        return jsonify({'key': meeting_request.id})
    else:
        meeting_request = MeetingRequest.query.filter(
            MeetingRequest.id == meeting_request_key).one()
        db.session.delete(meeting_request)
        db.session.commit()
        return jsonify({'key': ''})


@meeting_requests.route('/<meeting_spec_key>', methods=['GET'])
def get_meeting_request(meeting_spec_key):
    user = get_user(request.args.get('email'))
    meeting_spec = MeetingSpec.query.filter(
        MeetingSpec.id == int(meeting_spec_key)).first()
    meeting_request = query_meeting_request(meeting_spec, user)

    resp = jsonify({'key': meeting_request.id if meeting_request else ""})
    resp.status_code = 200
    return resp
