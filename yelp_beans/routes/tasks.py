# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging
from datetime import datetime
from datetime import timedelta

from flask import Blueprint

from yelp_beans.logic.data_ingestion import DataIngestion
from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.meeting_spec import get_specs_for_current_week
from yelp_beans.logic.subscription import get_specs_from_subscription
from yelp_beans.logic.subscription import store_specs_from_subscription
from yelp_beans.logic.user import sync_employees
from yelp_beans.matching.match import generate_meetings
from yelp_beans.matching.match_utils import save_meetings
from yelp_beans.models import Meeting
from yelp_beans.models import MeetingParticipant
from yelp_beans.models import MeetingRequest
from yelp_beans.models import MeetingSubscription
from yelp_beans.models import Rule
from yelp_beans.models import SubscriptionDateTime
from yelp_beans.send_email import send_batch_meeting_confirmation_email
from yelp_beans.send_email import send_batch_unmatched_email
from yelp_beans.send_email import send_batch_weekly_opt_in_email

tasks = Blueprint('tasks', __name__)


@tasks.route('/generate_meeting_specs_for_week', methods=['GET'])
def generate_meeting_specs():
    for subscription in MeetingSubscription.query().fetch():
        logging.info(subscription)
        week_start, specs = get_specs_from_subscription(subscription)
        store_specs_from_subscription(subscription.key, week_start, specs)
    return 'OK'


@tasks.route('/email_users_for_weekly_opt_in', methods=['GET'])
def weekly_opt_in():
    for spec in get_specs_for_current_week():
        logging.info(spec)
        send_batch_weekly_opt_in_email(spec)
    return 'OK'


@tasks.route('/populate_employees', methods=['GET'])
def populate_employees():
    employees = DataIngestion().ingest()
    sync_employees([employee for employee in employees])
    return "OK"


@tasks.route('/match_employees', methods=['GET'])
def match_employees():
    specs = get_specs_for_current_week()

    for spec in specs:
        logging.info('Spec Datetime: ')
        logging.info(get_meeting_datetime(spec).strftime("%Y-%m-%d %H:%M"))

        users = [
            request.user.get()
            for request
            in MeetingRequest.query(
                MeetingRequest.meeting_spec == spec.key
            ).fetch()
        ]
        logging.info('Users: ')
        logging.info([user.get_username() for user in users])

        group_size = spec.meeting_subscription.get().size
        matches, unmatched = generate_meetings(users, spec, prev_meeting_tuples=None, group_size=group_size)
        save_meetings(matches, spec)

        send_batch_unmatched_email(unmatched)
        send_batch_meeting_confirmation_email(matches, spec)
    return "OK"


@tasks.route('/send_match_email_for_week', methods=['GET'])
def send_match_emails():
    specs = get_specs_for_current_week()
    for spec in specs:
        matches = []
        meetings = Meeting.query(Meeting.meeting_spec == spec.key).fetch()
        for meeting in meetings:
            participants = MeetingParticipant.query(
                MeetingParticipant.meeting == meeting.key
            ).fetch()
            matches.append(
                (participants[0].user.get(), participants[1].user.get())
            )
        logging.info(spec)
        logging.info(matches)
        send_batch_meeting_confirmation_email(matches, spec)
    return "OK"


@tasks.route('/init', methods=['POST'])
def init():
    subscriptions = MeetingSubscription.query().fetch()
    if not subscriptions:
        preference_1 = SubscriptionDateTime(
            datetime=datetime.now()
        ).put()
        preference_2 = SubscriptionDateTime(
            datetime=datetime.now() + timedelta(days=1)
        ).put()
        rule = Rule(
            name='office',
            value='USA: CA SF New Montgomery Office'
        ).put()

        MeetingSubscription(
            title='Yelp Weekly',
            size=2,
            location='8th Floor',
            office='USA: CA SF New Montgomery Office',
            timezone='US/Pacific',
            datetime=[preference_1, preference_2],
            rules=[rule],
            rule_logic='any'
        ).put()
    return "OK"
