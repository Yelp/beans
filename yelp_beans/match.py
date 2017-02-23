# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import logging
from collections import defaultdict
from datetime import datetime
from datetime import timedelta

import networkx as nx

from yelp_beans.logic.config import get_config
from yelp_beans.logic.user import user_preference
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingSpec


def get_disallowed_meetings(users, prev_meeting_tuples, spec):
    """Returns set of matches that are not allowed
    Returns:
        Set of tuples
    """
    # don't match users with previous meetings
    pairs = prev_meeting_tuples

    userids = sorted([user.key.id() for user in users])
    id_to_user = {user.key.id(): user for user in users}
    all_pairs = {pair for pair in itertools.combinations(userids, 2)}

    # users aren't matched if they are on the same team
    pairs = pairs.union({pair for pair in all_pairs if is_same_team(pair, id_to_user)})

    return pairs


def is_same_team(match, users):
    return users[match[0]].metadata['department'] == users[match[1]].metadata['department']


def save_meetings(matches, spec):
    for match in matches:
        meeting_key = Meeting(meeting_spec=spec.key).put()
        MeetingParticipant(meeting=meeting_key, user=match[0].key).put()
        MeetingParticipant(meeting=meeting_key, user=match[1].key).put()
        logging.info(meeting_key)
        logging.info('{}, {}'.format(
            match[0].get_username(),
            match[1].get_username(),
        ))


def get_previous_meetings(cooldown=None):

    if cooldown is None:
        cooldown = get_config()['meeting_cooldown_weeks']

    meetings = defaultdict(list)

    # get all meeting specs from x weeks ago til now
    time_threshold_for_meetings = datetime.now() - timedelta(weeks=cooldown)

    meeting_spec_keys = [
        spec.key for spec in MeetingSpec.query(
            MeetingSpec.datetime > time_threshold_for_meetings
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


def generate_meetings(users, spec, prev_meeting_tuples=None):
    """
    Returns 2 tuples:
    - meetings: list of dicts of the same type as prev_meetings, to indicate
      this iteration's found meetings
    - unmatched_user_ids: users with no matches.
    """
    if prev_meeting_tuples is None:
        prev_meeting_tuples = get_previous_meetings()

    uid_to_users = {user.key.id(): user for user in users}
    user_ids = sorted(uid_to_users.keys())

    # Determine matches that should not happen
    disallowed_meeting_set = get_disallowed_meetings(
        users, prev_meeting_tuples, spec
    )
    graph_matches = construct_graph(user_ids, disallowed_meeting_set)

    # matching returns (1,4) and (4,1) this de-dupes
    graph_matches = dict((a, b) if a <= b else (b, a)
                         for a, b in graph_matches.iteritems())

    matches = []
    for uid_a, uid_b in graph_matches.items():
        user_a = uid_to_users[uid_a]
        user_b = uid_to_users[uid_b]
        time = user_preference(user_a, spec)
        matches.append((user_a, user_b, time))

    logging.info('{} employees matched'.format(len(matches) * 2))
    logging.info([(meeting[0].get_username(), meeting[1].get_username()) for meeting in matches])

    unmatched = [
        uid_to_users[user]
        for user in user_ids
        if user not in graph_matches.keys()
        if user not in graph_matches.values()
    ]

    logging.info('{} employees unmatched'.format(len(unmatched)))
    logging.info([user.get_username() for user in unmatched])

    return matches, unmatched


def construct_graph(user_ids, disallowed_meetings):
    """
    We can use a maximum matching algorithm for this:
    https://en.wikipedia.org/wiki/Blossom_algorithm
    Yay graphs! Networkx will do all the work for us.
    """

    # special weights that be put on the matching potential of each meeting,
    # depending on heuristics for what makes a good/bad potential meeting.
    meeting_to_weight = {}

    # This creates the graph and the maximal matching set is returned.
    # It does not return anyone who didn't get matched.
    meetings = []
    possible_meetings = {
        meeting for meeting in itertools.combinations(user_ids, 2)
    }
    allowed_meetings = possible_meetings - disallowed_meetings

    for meeting in allowed_meetings:
        weight = meeting_to_weight.get(meeting, 1.0)
        meetings.append(meeting + ({'weight': weight},))

    graph = nx.Graph()
    graph.add_nodes_from(user_ids)
    graph.add_edges_from(meetings)

    return nx.max_weight_matching(graph)
