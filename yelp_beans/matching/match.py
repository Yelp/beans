# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.matching.pair_match import generate_pair_meetings


def generate_meetings(users, spec, prev_meeting_tuples=None, group_size=2):
    if group_size == 2:
        return generate_pair_meetings(users, spec, prev_meeting_tuples)
    else:
        raise NotImplementedError("Group matching not implemented yet.")
