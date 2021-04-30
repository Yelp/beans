from collections import defaultdict

from sqlalchemy.orm import joinedload
from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.meeting_spec import get_specs_for_current_week
from yelp_beans.logic.meeting_spec import get_specs_for_current_week_query
from yelp_beans.logic.meeting_spec import get_users_from_spec
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSpec
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import UserSubscriptionPreferences


def get_subscribers():
    sub_prefs = UserSubscriptionPreferences.query.options(joinedload(UserSubscriptionPreferences.user)).all()
    subscriptions = MeetingSubscription.query.all()

    # creates metrics keys for all subscriptions including ones without users
    metrics = {subscription.id: [] for subscription in subscriptions}

    # creates metrics keys for all subscriptions that have users with user data
    for preference in sub_prefs:
        metrics[preference.subscription_id].append(preference.user.email)

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
    specs = get_specs_for_current_week_query().options(
        joinedload(MeetingSpec.meeting_subscription)
    ).all()
    spec_id_to_title = {
        spec.id: spec.meeting_subscription.title
        for spec in specs
    }

    meeting_requests = MeetingRequest.query.options(
        joinedload(MeetingRequest.user)
    ).filter(
        MeetingRequest.meeting_spec_id.in_([spec.id for spec in specs])
    ).all()

    for request in meeting_requests:
        request_title = spec_id_to_title[request.meeting_spec_id]
        requests.append(
            {
                'title': request_title,
                'user': request.user.email,
            }
        )
    return requests
