import pytest
from yelp_beans.logic.user import add_preferences
from yelp_beans.logic.user import create_new_employees_from_list
from yelp_beans.logic.user import hash_employee_data
from yelp_beans.logic.user import is_valid_user_subscription_preference
from yelp_beans.logic.user import mark_termed_employees
from yelp_beans.logic.user import remove_preferences
from yelp_beans.logic.user import sync_employees
from yelp_beans.logic.user import update_current_employees
from yelp_beans.logic.user import user_preference
from yelp_beans.logic.user import validate_employee_data
from yelp_beans.models import MeetingSpec
from yelp_beans.models import Rule
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def test_sync_creates_new_employee(database, data_source):
    """
    Data source contains a user that we don't have in our database,
    we must create a new user in our database.
    """
    sync_employees(data_source)
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert user.first_name == 'Sam'


def test_sync_marks_employee_as_terminated(database, data_source):
    """
    Data source contains a list of active users for beans.  If the user
    is not present in the data source, but present in our database we

    mark the employee as terminated
    """
    sync_employees(data_source)
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert not user.terminated

    sync_employees({})
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert user.terminated


def test_sync_updates_current_employee(database, data_source):
    """
    Data source contains a user that we are already tracking in our database,
    we must update the user in the database to reflect new information.
    Returns
    """
    sync_employees(data_source)
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert user.first_name == 'Sam'
    assert user.meta_data['department'] == 'Engineering'

    data = data_source[0]
    data['first_name'] = 'John'
    data['department'] = 'Design'
    data['metadata']['department'] = 'Design'
    sync_employees(data_source)
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert user.first_name == 'John'
    assert user.meta_data['department'] == 'Design'


def test_hash_employee_data(data_source, data_source_by_key):
    """
    Given a json object, return a dictionary by email of users.
    """
    employees = hash_employee_data(data_source)
    assert len(list(employees.keys())) == 2
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
    user = User.query.one()
    assert user.terminated


def test_create_new_employees_from_list(session, data_source):
    create_new_employees_from_list(data_source)
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert user.email == 'samsmith@yelp.com'
    assert user.meta_data == {
        'department': 'Engineering',
        'title': 'Engineer',
        'floor': '10',
        'desk': '100',
        'manager': 'Bo Demillo'
    }


def test_update_current_employees(session, data_source):
    create_new_employees_from_list(data_source)
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert user.photo_url == 'www.cdn.com/SamSmith.png'
    assert user.meta_data == {
        'department': 'Engineering',
        'title': 'Engineer',
        'floor': '10',
        'desk': '100',
        'manager': 'Bo Demillo'
    }

    local_data_employee = {user.email: user for user in User.query.all()}
    remote_data_employee = hash_employee_data(data_source)

    remote_data_employee['samsmith@yelp.com']['photo_url'] = 'new'
    remote_data_employee['samsmith@yelp.com']['department'] = 'Sales'
    remote_data_employee['samsmith@yelp.com']['metadata']['department'] = 'Sales'

    update_current_employees(local_data_employee, remote_data_employee)
    user = User.query.filter(User.email == 'samsmith@yelp.com').one()
    assert user.photo_url == 'new'
    assert user.meta_data['department'] == 'Sales'
    assert user.meta_data == {
        'department': 'Sales',
        'title': 'Engineer',
        'floor': '10',
        'desk': '100',
        'manager': 'Bo Demillo'
    }


def test_user_preference(session, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription,
    )
    session.add(user_pref)
    user = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    session.add(user)
    meeting_spec = MeetingSpec(meeting_subscription=subscription, datetime=subscription.datetime[0].datetime)
    session.add(meeting_spec)
    session.commit()

    assert user_pref == user_preference(user, meeting_spec)


def test_remove_preferences_removes_on_opt_out(session, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription,
    )
    session.add(user_pref)
    user = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    session.add(user)
    session.commit()

    assert user.subscription_preferences == [user_pref]
    updated_preferences = {preference.id: False}
    removed = remove_preferences(user, updated_preferences, subscription.id)
    assert removed == {user_pref.preference_id}
    user = User.query.filter(User.id == user.id).one()
    assert user.subscription_preferences == []
    assert UserSubscriptionPreferences.query.all() == []


def test_remove_preferences_does_not_remove_on_opt_in(session, subscription):
    preference = subscription.datetime[0]
    user_pref = UserSubscriptionPreferences(
        preference=preference,
        subscription=subscription,
    )
    session.add(user_pref)
    user = User(email='a@yelp.com', meta_data={'department': 'dept'}, subscription_preferences=[user_pref])
    session.add(user)
    session.commit()

    assert user.subscription_preferences == [user_pref]
    updated_preferences = {preference.id: True}
    removed = remove_preferences(user, updated_preferences, subscription)
    assert removed == set()
    user = User.query.filter(User.id == user.id).one()
    assert user.subscription_preferences == [user_pref]
    assert len(UserSubscriptionPreferences.query.all()) == 1


def test_remove_preferences_multiple_remove_on_opt_in(session, subscription):
    preference_1 = subscription.datetime[0]
    preference_2 = subscription.datetime[1]
    user_pref_1 = UserSubscriptionPreferences(
        preference=preference_1,
        subscription=subscription,
    )
    user_pref_2 = UserSubscriptionPreferences(
        preference=preference_2,
        subscription=subscription,
    )
    session.add(user_pref_1)
    session.add(user_pref_2)
    user = User(
        email='a@yelp.com',
        meta_data={'department': 'dept'},
        subscription_preferences=[user_pref_1, user_pref_2]
    )
    session.add(user)
    session.commit()

    assert user.subscription_preferences == [user_pref_1, user_pref_2]
    updated_preferences = {preference_1.id: False, preference_2.id: False}
    removed = remove_preferences(user, updated_preferences, subscription.id)
    assert removed == {user_pref_1.preference_id, user_pref_2.preference_id}
    user = user = User.query.filter(User.id == user.id).one()
    assert user.subscription_preferences == []
    assert UserSubscriptionPreferences.query.all() == []


def test_add_preferences_adds_on_opt_in(session, subscription):
    preference = subscription.datetime[0]
    user = User(email='a@yelp.com', meta_data={'department': 'dept'})
    session.add(user)
    session.commit()

    updated_preferences = {preference.id: {'enabled': True, 'autoRenew': False}}
    assert len(user.subscription_preferences) == 0
    added = add_preferences(user, updated_preferences, subscription.id)
    assert added.pop() == preference.id
    user = User.query.filter(User.id == user.id).one()
    assert user.subscription_preferences[0].preference == preference


def test_add_preferences_adds_multiple_on_opt_in(session, subscription):
    preference_1 = subscription.datetime[0]
    preference_2 = subscription.datetime[1]
    user = User(email='a@yelp.com', meta_data={'department': 'dept'})
    session.add(user)
    session.commit()

    updated_preferences = {preference_1.id: True, preference_2.id: True}
    assert len(user.subscription_preferences) == 0
    added = add_preferences(user, updated_preferences, subscription.id)
    assert preference_1.id in added
    assert preference_2.id in added
    assert len(user.subscription_preferences) == 2
    user = User.query.filter(User.id == user.id).one()
    assert user.subscription_preferences[0].preference in (preference_1, preference_2)
    assert user.subscription_preferences[1].preference in (preference_1, preference_2)


def test_is_valid_user_subscription_preference_no_subscription(subscription):
    preference = subscription.datetime[0]
    user = User(email='a@yelp.com', meta_data={'department': 'dept'})
    user_sub = UserSubscriptionPreferences(preference=preference, subscription_id=None, user=user)
    subscription.user_rules = [Rule(name='department', value='dept')]
    subscription.rule_logic = 'all'

    result = is_valid_user_subscription_preference(user_sub, None)
    assert not result


def test_is_valid_user_subscription_preference_user_terminated(subscription):
    preference = subscription.datetime[0]
    user = User(email='a@yelp.com', meta_data={'department': 'dept'}, terminated=True)
    user_sub = UserSubscriptionPreferences(preference=preference, subscription_id=subscription.id, user=user)
    subscription.user_rules = [Rule(name='department', value='dept')]
    subscription.rule_logic = 'all'

    result = is_valid_user_subscription_preference(user_sub, subscription)
    assert not result

def test_is_valid_user_subscription_preference_fails_rules(subscription):
    preference = subscription.datetime[0]
    user = User(email='a@yelp.com', meta_data={'department': 'dept'})
    user_sub = UserSubscriptionPreferences(preference=preference, subscription_id=subscription.id, user=user)
    subscription.user_rules = [Rule(name='department', value='other dept')]
    subscription.rule_logic = 'all'

    result = is_valid_user_subscription_preference(user_sub, subscription)
    assert not result


def test_is_valid_user_subscription_preference_valid(subscription):
    preference = subscription.datetime[0]
    user = User(email='a@yelp.com', meta_data={'department': 'dept'})
    user_sub = UserSubscriptionPreferences(preference=preference, subscription_id=subscription.id, user=user)
    subscription.user_rules = [Rule(name='department', value='dept')]
    subscription.rule_logic = 'all'

    result = is_valid_user_subscription_preference(user_sub, subscription)
    assert result
