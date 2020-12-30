from collections import defaultdict

from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.meeting_spec import get_specs_for_current_week
from yelp_beans.logic.meeting_spec import get_users_from_spec
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import User


def get_subscribers():
    users = User.query.all()
    subscriptions = MeetingSubscription.query.all()

    metrics = defaultdict(set)
    # creates metrics keys for all subscriptions including ones without users
    for subscription in subscriptions:
        metrics[subscription.id] = []

    # creates metrics keys for all subscriptions that have users with user data
    for user in users:
        for preference in user.subscription_preferences:
            metrics[preference.subscription_id].append(user.email)

    return metrics


def get_current_week_participation():
    participation = defaultdict(dict)

    for spec in get_specs_for_current_week():
        participation[spec.subscription_id][spec.id] = [
            user.get_username() for user in [_f for _f in get_users_from_spec(spec) if _f]
        ]

    return participation


def get_meeting_participants():
    meetings = defaultdict(list)
    participants = MeetingParticipant.query.all()
    for participant in participants:
        try:
            email = participant.user.email
            meeting_id = participant.meeting_id
            meetings[meeting_id].append(email)
        except AttributeError:
            pass

    metrics = []
    for meeting_id in meetings.keys():
        meeting_spec = Meeting.query.filter(Meeting.id == meeting_id).one().meeting_spec
        meeting_title = meeting_spec.meeting_subscription.title
        participants = meetings[meeting_id]
        for participant in participants:
            metrics.append(
                {
                    'participant': participant,
                    'meeting': meeting_id,
                    'meeting_title': meeting_title,
                    'date': meeting_spec.datetime.isoformat(),
                    'time': get_meeting_datetime(meeting_spec).strftime('%I:%M%p'),
                }
            )
    return metrics


def get_meeting_requests():
    requests = []
    for spec in get_specs_for_current_week():
        users = [
            request.user.email
            for request
            in MeetingRequest.query.filter(
                MeetingRequest.meeting_spec_id == spec.id
            ).all()
        ]
        for user in users:
            requests.append(
                {
                    'title': spec.meeting_subscription.title,
                    'user': user,
                }
            )
    return requests
