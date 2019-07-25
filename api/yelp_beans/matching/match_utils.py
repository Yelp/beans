# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

from google.appengine.ext import ndb
from yelp_beans.logic.config import get_config
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingSpec


def save_meetings(matches, spec):
    for match in matches:
        # Last element in match is the key for meeting time
        matched_users = match[:-1]
        meeting_key = Meeting(meeting_spec=spec.key).put()
        for user in matched_users:
            MeetingParticipant(meeting=meeting_key, user=user.key).put()
        username_list = [user.get_username() for user in matched_users]
        logging.info(meeting_key)
        logging.info(', '.join(username_list))


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
        cooldown = get_config()['meeting_cooldown_weeks']

    meetings = defaultdict(list)

    # get all meeting specs from x weeks ago til now
    time_threshold_for_meetings = datetime.now() - timedelta(weeks=cooldown)

    meeting_spec_keys = [
        spec.key for spec in MeetingSpec.query(
            ndb.AND(MeetingSpec.datetime > time_threshold_for_meetings,
                    MeetingSpec.meeting_subscription == subscription)
        ).fetch()
    ]

    logging.info('Previous Meeting History: ')
    logging.info([meeting.get().datetime.strftime("%Y-%m-%d %H:%M") for meeting in meeting_spec_keys])

    if meeting_spec_keys == []:
        return set([])

    # get all meetings from meeting specs
    meeting_keys = [meeting.key for meeting in Meeting.query().filter(
        Meeting.meeting_spec.IN(meeting_spec_keys)).fetch()]

    if meeting_keys == []:
        return set([])

    # get all participants from meetings
    participants = MeetingParticipant.query().filter(
        MeetingParticipant.meeting.IN(meeting_keys)
    ).fetch()

    if participants == []:
        return set([])

    # group by meeting Id
    for participant in participants:
        meetings[participant.meeting.id()].append(participant.user)

    # ids are sorted, all matches should be in increasing order by id for the matching algorithm to work
    disallowed_meetings = set([tuple(sorted(meeting, key=lambda Key: Key.id())) for meeting in meetings.values()])

    logging.info('Past Meetings')
    logging.info([tuple([meeting.get().get_username() for meeting in meeting]) for meeting in disallowed_meetings])

    disallowed_meetings = {tuple([meeting.id() for meeting in meeting]) for meeting in disallowed_meetings}

    return disallowed_meetings
