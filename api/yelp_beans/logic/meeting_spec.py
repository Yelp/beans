# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import datetime
from datetime import timedelta

from pytz import timezone
from pytz import utc
from yelp_beans.models import MeetingSpec
from yelp_beans.models import User
from yelp_beans.models import UserSubscriptionPreferences


def get_specs_for_current_week():
    week_start = datetime.now() - timedelta(days=datetime.now().weekday())
    week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    return MeetingSpec.query(MeetingSpec.datetime > week_start).fetch()


def get_users_from_spec(meeting_spec):
    logging.info('Meeting subscription for spec:')
    logging.info(meeting_spec.meeting_subscription)
    logging.info('All Preferences')
    logging.info(UserSubscriptionPreferences.query().fetch())

    user_sub_preferences = UserSubscriptionPreferences.query(
        UserSubscriptionPreferences.subscription == meeting_spec.meeting_subscription
    ).fetch()

    logging.info('User Preferences')
    logging.info(user_sub_preferences)
    users = []
    for user_preference in user_sub_preferences:

        if user_preference.preference:
            logging.info('User Preference')
            logging.info(user_preference.preference)
            logging.info(user_preference.preference.get())
            preference_dt = user_preference.preference.get().datetime

            if preference_dt.hour == meeting_spec.datetime.hour and \
                    preference_dt.minute == meeting_spec.datetime.minute and \
                    preference_dt.weekday() == meeting_spec.datetime.weekday():

                user = User.query(
                    User.subscription_preferences == user_preference.key).get()
                logging.info('user added: ')
                logging.info(user)
                users.append(user)

    return users


def get_meeting_datetime(meeting_spec):
    """
    Given a meeting_spec, returns the meeting datetime in the appropriate timezone.
    :param meeting_spec: models.meeting_spec
    :return: datetime.datetime in the correct timezone
    """
    meeting_datetime = meeting_spec.datetime

    meeting_timezone = meeting_spec.meeting_subscription.get().timezone
    return meeting_datetime.replace(tzinfo=utc).astimezone(timezone(meeting_timezone))
