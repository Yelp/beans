# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import itertools
import logging
import random

from yelp_beans.matching.match_utils import get_counts_for_pairs
from yelp_beans.matching.match_utils import get_previous_meetings


def get_previous_meetings_counts(users, subscription_key):
    """
    Given users for a subscription, return the number of times two people have matched
    :param users: id of user
    :param subscription_key: Key referencing the subscription model entity
    :return: Tuple of user id's matched to count ie. {(4L, 5L): 5}
    """
    previous_meetings = get_previous_meetings(subscription_key)
    counts_for_pairs = get_counts_for_pairs(previous_meetings)
    user_ids = sorted([user.key.id() for user in users])
    all_pairs_counts = {pair: 0 for pair in itertools.combinations(user_ids, 2)}
    for pair in counts_for_pairs:
        all_pairs_counts[pair] = counts_for_pairs[pair]
    return all_pairs_counts


def get_user_weights(users, previous_meetings_counts, starting_weight, negative_weight):
    """
    Given users asking for a match and historical information about the previous people they met,
    return weights to promote groups where people haven't met each other.
    :param users: list of user models
    :param previous_meetings_counts: tuple of user id's matched to count
    :param starting_weight: initial weight between users
    :param negative_weight: amount to subtract from initial weight based on previous meetings
    :return: adjacency matrix from user to user
    """
    user_user_weights = []
    for idx1, user1 in enumerate(users):
        user_user_weights.append([])
        for idx2, user2 in enumerate(users):
            pair_tuple = tuple(sorted((user1.key.id(), user2.key.id())))
            if pair_tuple not in previous_meetings_counts:
                user_user_weights[idx1].append(0)
                continue
            weight = starting_weight - (negative_weight * previous_meetings_counts[pair_tuple])
            user_user_weights[idx1].append(weight)
    return user_user_weights


def generate_groups(group, partition_size):
    """
    Given a group, partition into smaller groups of a specific size.  Zero
    for group size is invalid. Partitions will never exceed inputted value, but may be smaller.
    :param group: List of ids
    :param partition_size: Intended size for group
    :return: list of groups
    """
    for i in range(0, len(group), partition_size):
        yield group[i:i + partition_size if (i + partition_size) < len(group) else len(group)]


def generate_group_meetings(users, spec, group_size, starting_weight, negative_weight):
    population_size = len(users)

    # For group meetings we must have more than 2 users
    if population_size == 0:
        return [], []

    if population_size in (1, 2):
        return [], users

    previous_meetings_counts = get_previous_meetings_counts(users, spec.meeting_subscription)
    adj_matrix = get_user_weights(users, previous_meetings_counts, starting_weight, negative_weight)
    annealing = Annealing(population_size, group_size, adj_matrix)
    grouped_ids = generate_groups(annealing.simulated_annealing(), group_size)

    matches = []
    unmatched = []
    for group in grouped_ids:
        grouped_users = [users[index] for index in group]
        if len(grouped_users) < group_size:
            unmatched.extend(grouped_users)
        else:
            matches.append(grouped_users)
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
