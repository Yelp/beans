import logging
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

from database import db

from yelp_beans.logic.config import get_config
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingSpec
from yelp_beans.models import User


def save_meetings(matches, spec):
    for match in matches:
        # Last element in match may be the key for meeting time
        matched_users = [user for user in match if isinstance(user, User)]
        meeting_key = Meeting(meeting_spec=spec)
        db.session.add(meeting_key)
        for user in matched_users:
            mp = MeetingParticipant(meeting=meeting_key, user=user)
            db.session.add(mp)
        db.session.commit()
        username_list = [user.get_username() for user in matched_users]
        logging.info(meeting_key)
        logging.info(", ".join(username_list))


def get_counts_for_pairs(pairs):
    counts = {}
    for pair in pairs:
        if pair in counts:
            counts[pair] += 1
        else:
            counts[pair] = 1
    return counts


def get_previous_meetings(subscription, cooldown=None):
    if cooldown is None:
        cooldown = get_config()["meeting_cooldown_weeks"]

    meetings = defaultdict(list)

    # get all meeting specs from x weeks ago til now
    time_threshold_for_meetings = datetime.now() - timedelta(weeks=cooldown)

    meeting_specs = [
        spec
        for spec in MeetingSpec.query.filter(
            MeetingSpec.datetime > time_threshold_for_meetings, MeetingSpec.meeting_subscription_id == subscription.id
        ).all()
    ]

    logging.info("Previous Meeting History: ")
    logging.info([meeting.datetime.strftime("%Y-%m-%d %H:%M") for meeting in meeting_specs])

    if meeting_specs == []:
        return set([])

    # get all meetings from meeting specs
    meeting_keys = [
        meeting.id for meeting in Meeting.query.filter(Meeting.meeting_spec_id.in_([meet.id for meet in meeting_specs])).all()
    ]

    if meeting_keys == []:
        return set([])

    # get all participants from meetings
    participants = MeetingParticipant.query.filter(MeetingParticipant.meeting_id.in_(meeting_keys)).all()

    if participants == []:
        return set([])

    # group by meeting Id
    for participant in participants:
        meetings[participant.meeting.id].append(participant.user)

    # ids are sorted, all matches should be in increasing order by id for the matching algorithm to work
    disallowed_meetings = set([tuple(sorted(meeting, key=lambda Key: Key.id)) for meeting in meetings.values()])

    logging.info("Past Meetings")
    logging.info([tuple([meeting.get_username() for meeting in meeting]) for meeting in disallowed_meetings])

    disallowed_meetings = {tuple([meeting.id for meeting in meeting]) for meeting in disallowed_meetings}

    return disallowed_meetings
