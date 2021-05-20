import logging
from typing import Optional

from database import db
from yelp_beans.logic.subscription import apply_rules
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def get_user(email):
    return User.query.filter(User.email == email).first()


def bulk_insert(data):
    db.session.add_all(data)
    db.session.commit()


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
        for employee in User.query.all()
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
        termed_employees_db = [local_employee_data[employee]
                               for employee in termed_employees]
        mark_termed_employees(termed_employees_db)
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
            meta_data=new_employee['metadata'],
            subscription_preferences=[],
        )
        user_list.append(user)
    bulk_insert(user_list)


def update_current_employees(local_data_employee, remote_data_employee):
    users = set(local_data_employee.keys())
    for user in users:
        local_employee = local_data_employee[user]
        remote_employee = remote_data_employee[user]

        local_employee.first_name = remote_employee['first_name']
        local_employee.last_name = remote_employee['last_name']
        local_employee.photo_url = remote_employee['photo_url']
        local_employee.meta_data = remote_employee['metadata']
        local_employee.terminated = False

    db.session.commit()


def mark_termed_employees(termed_employees):
    for employee in termed_employees:
        employee.terminated = True

    db.session.commit()


def user_preference(user, meeting_spec):
    preference_for_spec = [
        user_sub_pref
        for user_sub_pref in user.subscription_preferences
        if meeting_spec.meeting_subscription_id == user_sub_pref.subscription_id
    ]
    if preference_for_spec:
        return preference_for_spec[0]
    else:
        return None


def same_user_preference(user_a, user_b, spec):
    return user_preference(user_a, spec) == user_preference(user_b, spec)


def remove_preferences(user, updated_preferences, subscription_id):
    """
    Parameters
    ----------
    user - db.User
    preferences - {SubscriptionDateTime.id:Boolean}
    subscription_id - int

    Returns
    -------
    set(SubscriptionDateTime.id)

    """
    removed = set()
    for preference in user.subscription_preferences:
        if preference.subscription.id == subscription_id:
            if not updated_preferences.get(preference.preference_id, True):
                removed.add(preference.preference_id)
                db.session.delete(preference)

    db.session.commit()

    return removed


def add_preferences(user, updated_preferences, subscription_id):
    """
    Parameters
    ----------
    user - db.User
    preferences - {SubscriptionDateTime.id:Boolean}
    subscription_id - int

    Returns
    -------
    set(SubscriptionDateTime.id)
    """
    added = set()
    for datetime_id, active in updated_preferences.items():
        if active:
            preference = UserSubscriptionPreferences(
                subscription_id=subscription_id,
                preference_id=datetime_id,
            )
            db.session.add(preference)
            user.subscription_preferences.append(preference)
            db.session.add(user)
            added.add(datetime_id)
    db.session.commit()
    return added


def is_valid_user_subscription_preference(
    preference: UserSubscriptionPreferences,
    subscription: Optional[MeetingSubscription],
) -> bool:
    if preference.subscription_id is None:
        return False

    if preference.user.terminated:
        return False

    approved = apply_rules(preference.user, subscription, subscription.user_rules)
    return approved is not None


def delete_user_subscription_preference(preference: UserSubscriptionPreferences) -> bool:
    db.session.delete(preference)
    db.session.commit()
