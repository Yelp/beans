# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import itertools

from yelp_beans.matching.match_utils import get_counts_for_pairs
from yelp_beans.matching.match_utils import get_previous_meetings


def get_previous_meetings_counts(users, subscription):
    previous_meetings = get_previous_meetings(subscription)
    counts_for_pairs = get_counts_for_pairs(previous_meetings)
    userids = sorted([user.key.id() for user in users])
    all_pairs_counts = {pair: 0 for pair in itertools.combinations(userids, 2)}
    for pair in counts_for_pairs:
        all_pairs_counts[pair] = counts_for_pairs[pair]
    return all_pairs_counts
