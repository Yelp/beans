# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import pytest
from yelp_beans.logic.user import add_preferences
from yelp_beans.logic.user import create_new_employees_from_list
from yelp_beans.logic.user import hash_employee_data
from yelp_beans.logic.user import mark_termed_employees
from yelp_beans.logic.user import remove_preferences
from yelp_beans.logic.user import sync_employees
from yelp_beans.logic.user import update_current_employees
from yelp_beans.logic.user import user_preference
from yelp_beans.logic.user import validate_employee_data
from yelp_beans.models import MeetingSpec
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def test_sync_creates_new_employee(database, data_source):
    """
    Data source contains a user that we don't have in our database,
    we must create a new user in our database.
    """
    sync_employees(data_source)
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert user.first_name == 'Sam'


def test_sync_marks_employee_as_terminated(database, data_source):
    """
    Data source contains a list of active users for beans.  If the user
    is not present in the data source, but present in our database we

    mark the employee as terminated
    """
    sync_employees(data_source)
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert not user.terminated

    sync_employees({})
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert user.terminated


def test_sync_updates_current_employee(database, data_source):
    """
    Data source contains a user that we are already tracking in our database,
    we must update the user in the database to reflect new information.
    Returns
    """
    sync_employees(data_source)
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert user.first_name == 'Sam'
    assert user.metadata['department'] == 'Engineering'

    data = data_source[0]
    data['first_name'] = 'John'
    data['department'] = 'Design'
    data['metadata']['department'] = 'Design'
    sync_employees(data_source)
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert user.first_name == 'John'
    assert user.metadata['department'] == 'Design'


def test_hash_employee_data(data_source, data_source_by_key):
    """
    Given a json object, return a dictionary by email of users.
    """
    employees = hash_employee_data(data_source)
    assert len(employees.keys()) == 2
    assert set(employees.keys()) == {'samsmith@yelp.com', 'derrickjohnson@yelp.com'}
    assert employees['samsmith@yelp.com']['last_name'] == 'Smith'


def test_hash_employee_data_errors_with_no_email(data_source, data_source_by_key):
    data = data_source
    del data[0]['email']
    with pytest.raises(KeyError):
        hash_employee_data(data)


def test_validate_employee_data(data_source):
    data = data_source
    validate_employee_data(data)

    # raises without email
    with pytest.raises(KeyError):
        data = data_source
        del data[0]['email']
        validate_employee_data(data)

    # raises without first name
    with pytest.raises(KeyError):
        data = data_source
        del data[0]['first_name']
        validate_employee_data(data)

    # raises without last name
    with pytest.raises(KeyError):
        data = data_source
        del data[0]['last_name']
        validate_employee_data(data)


def test_mark_terminated_employees(database, fake_user):
    mark_termed_employees([fake_user])
    user = User.query().get()
    assert user.terminated


def test_create_new_employees_from_list(minimal_database, data_source):
    create_new_employees_from_list(data_source)
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert user.email == 'samsmith@yelp.com'
    assert user.metadata == {
        'department': 'Engineering',
        'title': 'Engineer',
        'floor': '10',
        'desk': '100',
        'manager': 'Bo Demillo'
    }


def test_update_current_employees(minimal_database, data_source):
    create_new_employees_from_list(data_source)
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert user.photo_url == 'www.cdn.com/SamSmith.png'
    assert user.metadata == {
        'department': 'Engineering',
        'title': 'Engineer',
        'floor': '10',
        'desk': '100',
        'manager': 'Bo Demillo'
    }

    local_data_employee = {user.email: user for user in User.query().fetch()}
    remote_data_employee = hash_employee_data(data_source)

    remote_data_employee['samsmith@yelp.com']['photo_url'] = 'new'
    remote_data_employee['samsmith@yelp.com']['department'] = 'Sales'
    remote_data_employee['samsmith@yelp.com']['metadata']['department'] = 'Sales'

    update_current_employees(local_data_employee, remote_data_employee)
    user = User.query(User.email == 'samsmith@yelp.com').get()
    assert user.photo_url == 'new'
    assert user.metadata['department'] == 'Sales'
    assert user.metadata == {
        'department': 'Sales',
        'title': 'Engineer',
        'floor': '10',
        'desk': '100',
        'manager': 'Bo Demillo'
    }


def test_user_preference(minimal_database, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription.key,
    ).put()
    user = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user.put()
    meeting_spec = MeetingSpec(meeting_subscription=subscription.key, datetime=subscription.datetime[0].get().datetime)
    meeting_spec.put()

    assert user_pref == user_preference(user, meeting_spec)


def test_remove_preferences_removes_on_opt_out(minimal_database, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription.key,
    ).put()
    user = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user.put()

    assert user.subscription_preferences == [user_pref]
    updated_preferences = {preference: False}
    removed = remove_preferences(user, updated_preferences, subscription.key)
    assert removed == {user_pref}
    user = user.key.get()
    assert user.subscription_preferences == []
    assert UserSubscriptionPreferences.query().fetch() == []


def test_remove_preferences_does_not_remove_on_opt_in(minimal_database, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription.key,
    ).put()
    user = User(email='a@yelp.com', metadata={'department': 'dept'}, subscription_preferences=[user_pref])
    user.put()

    assert user.subscription_preferences == [user_pref]
    updated_preferences = {preference: True}
    removed = remove_preferences(user, updated_preferences, subscription.key)
    assert removed == set()
    user = user.key.get()
    assert user.subscription_preferences == [user_pref]
    assert len(UserSubscriptionPreferences.query().fetch()) == 1


def test_remove_preferences_multiple_remove_on_opt_in(minimal_database, subscription):
    preference_1 = subscription.datetime[0]
    preference_2 = subscription.datetime[1]
    user_pref_1 = UserSubscriptionPreferences(
        preference=preference_1,
        subscription=subscription.key,
    ).put()
    user_pref_2 = UserSubscriptionPreferences(
        preference=preference_2,
        subscription=subscription.key,
    ).put()
    user = User(
        email='a@yelp.com',
        metadata={'department': 'dept'},
        subscription_preferences=[user_pref_1, user_pref_2]
    )
    user.put()

    assert user.subscription_preferences == [user_pref_1, user_pref_2]
    updated_preferences = {preference_1: False, preference_2: False}
    removed = remove_preferences(user, updated_preferences, subscription.key)
    assert removed == {user_pref_1, user_pref_2}
    user = user.key.get()
    assert user.subscription_preferences == []
    assert UserSubscriptionPreferences.query().fetch() == []


def test_add_preferences_adds_on_opt_in(minimal_database, subscription):
    preference = subscription.datetime[0]
    user = User(email='a@yelp.com', metadata={'department': 'dept'})
    user.put()

    updated_preferences = {preference: True}
    assert len(user.subscription_preferences) == 0
    added = add_preferences(user, updated_preferences, subscription.key)
    assert added.pop() == preference
    assert user.key.get().subscription_preferences[0].get().preference == preference


def test_add_preferences_adds_multiple_on_opt_in(minimal_database, subscription):
    preference_1 = subscription.datetime[0]
    preference_2 = subscription.datetime[1]
    user = User(email='a@yelp.com', metadata={'department': 'dept'})
    user.put()

    updated_preferences = {preference_1: True, preference_2: True}
    assert len(user.subscription_preferences) == 0
    added = add_preferences(user, updated_preferences, subscription.key)
    assert preference_1 in added
    assert preference_2 in added
    assert len(user.subscription_preferences) == 2
    assert user.key.get().subscription_preferences[0].get().preference in (preference_1, preference_2)
    assert user.key.get().subscription_preferences[1].get().preference in (preference_1, preference_2)
