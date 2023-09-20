from database import db

from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSpec
from yelp_beans.models import User


def store_meeting_request(meeting_request: MeetingRequest) -> int:
    """
    Parameters
    ----------
    meeting_request - MeetingRequest

    Returns
    -------
    MeetingRequest.id
    """

    db.session.add(meeting_request)
    db.session.commit()

    return meeting_request.id


def query_meeting_request(meeting_spec: MeetingSpec, user: User) -> MeetingRequest:
    """
    Parameters
    ----------
    meeting_spec - MeetingSpec
    user - User

    Returns
    -------
    MeetingRequest
    """

    return MeetingRequest.query.filter(
        MeetingRequest.meeting_spec_id == meeting_spec.id, MeetingRequest.user_id == user.id
    ).first()
