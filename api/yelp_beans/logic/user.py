# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

from google.appengine.api import users as google_user_api
from google.appengine.ext import ndb
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def get_user(email=None):
    if email is None:
        current_user = google_user_api.get_current_user()
        email = current_user.email()

    return User.query(User.email == email).get()


def sync_employees(employee_data):
    """
    Employee data must include:
        - email
        - first_name
        - last_name
        - photo_url
    All other information will be included in the data store as
    metadata.

    Parameters
    ----------
    remote_data = json

    Returns
    -------
    success: integer, 0 successful, 1 failure
    """
    validate_employee_data(employee_data)
    remote_employee_data = hash_employee_data(employee_data)

    # get data from local database
    local_employee_data = {
        employee.email: employee
        for employee in User.query().fetch()
    }

    local_employees = set(local_employee_data.keys())
    remote_employees = set(remote_employee_data.keys())

    new_employees = remote_employees - local_employees
    if new_employees:
        logging.info('Creating new employees.')
        new_employees_list = [remote_employee_data[employee]
                              for employee in new_employees]
        create_new_employees_from_list(new_employees_list)
        logging.info('{} employees added'.format(len(new_employees)))
        logging.info(new_employees)

    termed_employees = local_employees - remote_employees
    if termed_employees:
        logging.info('Marking termed employees')
        termed_employees_ndb = [local_employee_data[employee]
                                for employee in termed_employees]
        mark_termed_employees(termed_employees_ndb)
        logging.info('{} employees marked as termed'.format(
            len(termed_employees)))
        logging.info(termed_employees)

    current_employees = remote_employees.intersection(local_employees)
    if current_employees:
        logging.info('Updating current employees')
        remote_employee_data = {
            employee: remote_employee_data[employee] for employee in current_employees}
        local_employee_data = {
            employee: local_employee_data[employee] for employee in current_employees}
        update_current_employees(local_employee_data, remote_employee_data)
        logging.info('{} employees updated'.format(len(current_employees)))
        logging.info(current_employees)


def hash_employee_data(employee_data):
    """
    Hashes employee data by email for quick lookup.  This is
    necessary for efficient comparison of remote and local data.
    Returns
    -------
    Dictionary - employee email to employee_data
    """
    email_to_employee = {}
    for employee in employee_data:
        email_to_employee[employee['email']] = employee
    return email_to_employee


def validate_employee_data(employee_data):
    """
    Beans requires users to supply a minimal set of data:
        - email
        - first_name
        - last_name

    ValueError raised if the above values do not exist.

    Parameters
    ----------
    employee_data - json object
    """
    for employee in employee_data:
        employee['email']
        employee['first_name']
        employee['last_name']
        employee['photo_url']


def create_new_employees_from_list(new_employees):
    user_list = []
    for new_employee in new_employees:
        user = User(
            email=new_employee['email'],
            first_name=new_employee['first_name'],
            last_name=new_employee['last_name'],
            photo_url=new_employee['photo_url'],
            metadata=new_employee['metadata'],
            subscription_preferences=[],
        )
        user_list.append(user)
    ndb.put_multi(user_list)


def update_current_employees(local_data_employee, remote_data_employee):
    users = set(local_data_employee.keys())
    for user in users:
        local_employee = local_data_employee[user]
        remote_employee = remote_data_employee[user]

        local_employee.first_name = remote_employee['first_name']
        local_employee.last_name = remote_employee['last_name']
        local_employee.photo_url = remote_employee['photo_url']
        local_employee.metadata = remote_employee['metadata']
        local_employee.terminated = False

    ndb.put_multi(local_data_employee.values())


def mark_termed_employees(termed_employees):
    for employee in termed_employees:
        employee.terminated = True

    ndb.put_multi(termed_employees)


def user_preference(user, meeting_spec):
    preference_for_spec = [
        user_sub_pref
        for user_sub_pref in user.subscription_preferences
        if meeting_spec.meeting_subscription == user_sub_pref.get().subscription
    ]
    if preference_for_spec:
        return preference_for_spec[0]
    else:
        return None


def same_user_preference(user_a, user_b, spec):
    return user_preference(user_a, spec) == user_preference(user_b, spec)


def remove_preferences(user, updated_preferences, subscription_key):
    """
    Parameters
    ----------
    user - ndb.User
    preferences - {SubscriptionDateTime.key:Boolean}
    subscription_key - ndb.Key

    Returns
    -------
    set(SubscriptionDateTime.Key)

    """
    removed = set()
    for preference in ndb.get_multi(user.subscription_preferences):
        if preference.subscription == subscription_key:
            if not updated_preferences.get(preference.preference, True):
                index = user.subscription_preferences.index(preference.key)
                removed.add(user.subscription_preferences[index])
                del user.subscription_preferences[index]
                user.put()

    for record in removed:
        record.delete()

    return removed


def add_preferences(user, updated_preferences, subscription_key):
    """
    Parameters
    ----------
    user - ndb.User
    preferences - {SubscriptionDateTime.key.urlsafe():Boolean}
    subscription_key - ndb.Key

    Returns
    -------
    set(SubscriptionDateTime.Key)
    """
    added = set()
    for datetime_key, active in updated_preferences.items():
        if active:
            preference = UserSubscriptionPreferences(
                subscription=subscription_key,
                preference=datetime_key,
            ).put()
            user.subscription_preferences.append(preference)
            user.put()
            added.add(datetime_key)
    return added
