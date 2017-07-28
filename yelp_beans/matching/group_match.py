# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import logging
import random

from yelp_beans.logic.user import user_preference
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


def get_adj_matrix(users, previous_meetings_counts, starting_weight, negative_weight):
    adj_matrix = []
    for idx1, user1 in enumerate(users):
        adj_matrix.append([])
        for idx2, user2 in enumerate(users):
            pair_tuple = tuple(sorted((user1.key.id(), user2.key.id())))
            if pair_tuple not in previous_meetings_counts:
                adj_matrix[idx1].append(0)
                continue
            weight = starting_weight - (negative_weight * previous_meetings_counts[pair_tuple])
            adj_matrix[idx1].append(weight)
    return adj_matrix


def chunk(input_list, chunk_size):
    for i in range(0, len(input_list), chunk_size):
        yield input_list[i:i + chunk_size if (i + chunk_size) < len(input_list) else len(input_list)]


def generate_group_meetings(users, spec, group_size, starting_weight, negative_weight):
    population_size = len(users)
    previous_meetings_counts = get_previous_meetings_counts(users, spec.meeting_subscription)
    adj_matrix = get_adj_matrix(users, previous_meetings_counts, starting_weight, negative_weight)
    annealing = Annealing(population_size, group_size, adj_matrix)
    grouped_ids = chunk(annealing.simulated_annealing(), group_size)

    matches = []
    unmatched = []
    for group in grouped_ids:
        group_users = [users[idx] for idx in group]
        if len(group) < group_size:
            unmatched.extend(group_users)
            continue
        time = user_preference(users[0], spec)
        group_users.append(time)
        users_time_tuple = tuple(group_users)
        matches.append(users_time_tuple)
    logging.info('{} employees matched'.format(len(matches) * group_size))
    for group in matches:
        username_tuple = tuple([user.get_username() for user in group[:-1]])
        logging.info(username_tuple)

    logging.info('{} employees unmatched'.format(len(unmatched)))
    logging.info([user.get_username() for user in unmatched])

    return matches, unmatched


class Annealing:
    def __init__(self, population_size, group_size, adj_matrix, max_iterations=100):
        self.population_size = population_size
        self.group_size = group_size
        self.adj_matrix = adj_matrix
        self.max_iterations = max_iterations

    def get_initial_state(self):
        ids = [i for i in range(self.population_size)]
        random.shuffle(ids)
        return State(self.population_size, self.group_size, ids)

    def get_temp(self, iteration):
        return 1.0 - (self.max_iterations - iteration) / (self.max_iterations + iteration)

    def simulated_annealing(self):
        prev_state = self.get_initial_state()
        best_state = prev_state.copy()

        best_cost = prev_cost = prev_state.get_cost(self.adj_matrix)

        for iteration in range(self.max_iterations):
            temp = self.get_temp(iteration)

            curr_state = prev_state.get_mutated_state()
            curr_cost = curr_state.get_cost(self.adj_matrix)

            if curr_cost > best_cost:
                best_cost = curr_cost
                best_state = curr_state

            if curr_cost > prev_cost or 1.0 * curr_cost / (prev_cost + 1) * temp < random.random():
                prev_cost = curr_cost
                prev_state = curr_state

        return best_state.ids


class State:
    def __init__(self, population_size, group_size, ids):
        self.population_size = population_size
        self.group_size = group_size
        self.ids = ids

    def copy(self):
        return State(self.population_size, self.group_size, self.ids[:])

    def get_cost(self, adj_matrix):
        cost = 0
        for i in range(0, len(self.ids), self.group_size):
            cost += sum([
                adj_matrix[edge[0]][edge[1]]
                for edge in itertools.combinations(self.ids[i:i + self.group_size], 2)
            ])
        return cost

    def get_mutated_state(self):
        x = random.randint(0, len(self.ids) - 1)
        y = random.randint(0, len(self.ids) - 2)
        if y >= x:
            y += 1

        ids = self.ids[:]
        ids[x], ids[y] = ids[y], ids[x]
        return State(
            self.population_size,
            self.group_size,
            ids
        )
