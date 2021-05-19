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
    sub_prefs = UserSubscriptionPreferences.query.options(
        joinedload(UserSubscriptionPreferences.user),
    ).filter(
        UserSubscriptionPreferences.subscription_id.isnot(None),
    ).all()
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
    # We are looking at all meetings and every subscription is likely to have a
    # meeting, so we should need all subscription information. We could load this
    # through a db join, but that makes the query more expensive and returns a lot
    # duplicate data since there should always be more meetings then subscriptions.
    # Doing the join in python allows us to get the data only once and shouldn't
    # require us getting more data than needed
    subscription_id_to_subscription = {
        meet_sub.id: meet_sub
        for meet_sub in MeetingSubscription.query.all()
    }

    participants = MeetingParticipant.query.options(
        joinedload(MeetingParticipant.user),
        joinedload(MeetingParticipant.meeting).joinedload(Meeting.meeting_spec),
    ).all()

    metrics = []
    for participant in participants:
        meeting_spec = participant.meeting.meeting_spec
        meeting_subscription = subscription_id_to_subscription[meeting_spec.meeting_subscription_id]
        meeting_title = meeting_subscription.title
        metrics.append(
            {
                'participant': participant.user.email,
                'meeting': participant.meeting.id,
                'meeting_title': meeting_title,
                'date': meeting_spec.datetime.isoformat(),
                'time': get_meeting_datetime(meeting_spec, meeting_subscription.timezone).strftime('%I:%M%p'),
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
