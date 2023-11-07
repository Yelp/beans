import itertools
import logging

import networkx as nx

from yelp_beans.logic.user import user_preference
from yelp_beans.matching.match_utils import get_meeting_weights
from yelp_beans.matching.match_utils import get_previous_meetings


def get_disallowed_meetings(users, prev_meeting_tuples, spec):
    """Returns set of matches that are not allowed
    Returns:
        Set of tuples
    """
    # don't match users with previous meetings
    pairs = prev_meeting_tuples

    userids = sorted([user.work_email for user in users])
    id_to_user = {user.work_email: user for user in users}
    all_pairs = {pair for pair in itertools.combinations(userids, 2)}

    # Debugging message
    print(f"get_disallowed_meetings: users: {users}")
    for rule in spec.meeting_subscription.dept_rules:
        pairs = pairs.union({pair for pair in all_pairs if is_same(rule.name, pair, id_to_user)})
        # print(f"get_disallowed_meetings: rule: {rule.name}")
        # print(f"get_disallowed_meetings: pairs: {pairs}")
    return pairs


def is_same(field, match, users):
    return getattr(users[match[0]],field) == getattr(users[match[1]], field)


def generate_pair_meetings(users, spec, prev_meeting_tuples=None):
    """
    Returns 2 tuples:
    - meetings: list of dicts of the same type as prev_meetings, to indicate
      this iteration's found meetings
    - unmatched_user_ids: users with no matches.
    """
    if prev_meeting_tuples is None:
        prev_meeting_tuples = get_previous_meetings(spec.meeting_subscription)

    uid_to_users = {user.work_email: user for user in users}
    user_ids = sorted(uid_to_users.keys())
    # print(f"generate_pair_meetings: user: {users}")
    # print(f"generate_pair_meetings: USER_IDs: {user_ids}")

    # Determine matches that should not happen
    disallowed_meeting_set = get_disallowed_meetings(users, prev_meeting_tuples, spec)
    # print(f"generate_pair_meetings: disallowed_meeting_set:{disallowed_meeting_set}")
    # print(f"generate_pair_meetings: user_ids:{user_ids}")
    graph_matches = construct_graph(user_ids, disallowed_meeting_set)

    # matching returns (1,4) and (4,1) this de-dupes
    graph_matches = dict((a, b) if a <= b else (b, a) for a, b in graph_matches)

    matches = []
    for uid_a, uid_b in graph_matches.items():
        user_a = uid_to_users[uid_a]
        user_b = uid_to_users[uid_b]
        time = user_preference(user_a, spec)
        matches.append((user_a, user_b, time))

    logging.info("{} employees matched".format(len(matches) * 2))
    logging.info([(meeting[0].get_username(), meeting[1].get_username()) for meeting in matches])

    unmatched = [
        uid_to_users[user]
        for user in user_ids
        if user not in list(graph_matches.keys())
        if user not in list(graph_matches.values())
    ]

    logging.info(f"{len(unmatched)} employees unmatched")
    logging.info([user.employee_id for user in unmatched])
    # print(f"generate_pair_meetings, matches: {matches}, unmatches: {unmatched}")
    return matches, unmatched


def construct_graph(user_ids, disallowed_meetings):
    """
    We can use a maximum matching algorithm for this:
    https://en.wikipedia.org/wiki/Blossom_algorithm
    Yay graphs! Networkx will do all the work for us.
    """

    # This creates the graph and the maximal matching set is returned.
    # It does not return anyone who didn't get matched.
    meetings = []
    possible_meetings = {tuple(sorted(meeting)) for meeting in itertools.combinations(user_ids, 2)}
    print(f"construct_graph, user_ids: {user_ids}")
    print(f"construct_graph, disallowed_meetings: {disallowed_meetings}")
    print(f"construct_graph, possible_meetings: {possible_meetings}")
    allowed_meetings = possible_meetings - {tuple(sorted(a)) for a in disallowed_meetings}

    print(f"construct_graph, allowed_meetings: {allowed_meetings}")

    # special weights that be put on the matching potential of each meeting,
    # depending on heuristics for what makes a good/bad potential meeting.
    meeting_to_weight = get_meeting_weights(allowed_meetings)

    for meeting in allowed_meetings:
        weight = meeting_to_weight.get(meeting, 1.0)
        meetings.append((*meeting, {"weight": weight}))

    graph = nx.Graph()
    graph.add_nodes_from(user_ids)
    graph.add_edges_from(meetings)

    return nx.max_weight_matching(graph)
