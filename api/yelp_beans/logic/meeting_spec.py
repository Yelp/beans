import logging
from datetime import datetime
from datetime import timedelta
from typing import Optional

from pytz import timezone
from pytz import utc
from yelp_beans.models import MeetingSpec
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def get_specs_for_current_week_query():
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    return MeetingSpec.query.filter(MeetingSpec.datetime > week_start)


def get_specs_for_current_week():
    return get_specs_for_current_week_query().all()


def get_users_from_spec(meeting_spec):
    logging.info('Meeting subscription for spec:')
    logging.info(meeting_spec.meeting_subscription)
    logging.info('All Preferences')
    logging.info(UserSubscriptionPreferences.query.all())

    user_sub_preferences = UserSubscriptionPreferences.query.filter(
        UserSubscriptionPreferences.subscription_id == meeting_spec.meeting_subscription_id
    ).all()

    logging.info('User Preferences')
    logging.info(user_sub_preferences)
    meeting_timezone = timezone(meeting_spec.meeting_subscription.timezone)
    users = []
    for user_preference in user_sub_preferences:

        if user_preference.preference:
            logging.info('User Preference')
            logging.info(user_preference.preference)
            logging.info(user_preference.preference.__dict__)
            preference_dt = user_preference.preference.datetime.replace(tzinfo=utc).astimezone(meeting_timezone)
            meeting_spec_dt = meeting_spec.datetime.replace(tzinfo=utc).astimezone(meeting_timezone)

            if preference_dt.hour == meeting_spec_dt.hour and \
                    preference_dt.minute == meeting_spec_dt.minute and \
                    preference_dt.weekday() == meeting_spec_dt.weekday():

                user = User.query.filter(
                    User.id == user_preference.user_id).one()
                logging.info('user added: ')
                logging.info(user)
                users.append(user)

    return users


def get_meeting_datetime(meeting_spec: MeetingSpec, subscription_timezone: Optional[str] = None) -> datetime:
    """
    Given a meeting_spec, returns the meeting datetime in the appropriate timezone.
    :param meeting_spec: models.meeting_spec
    :return: datetime.datetime in the correct timezone
    """
    meeting_datetime = meeting_spec.datetime

    if subscription_timezone is None:
        meeting_timezone = meeting_spec.meeting_subscription.timezone
    else:
        meeting_timezone = subscription_timezone
    return meeting_datetime.replace(tzinfo=utc).astimezone(timezone(meeting_timezone))
