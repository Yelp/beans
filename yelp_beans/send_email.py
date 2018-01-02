# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import json
import logging
import urllib

from jinja2 import Environment
from jinja2 import PackageLoader
from sendgrid import SendGridAPIClient
from sendgrid.helpers import mail
from sendgrid.helpers.mail import Content

from yelp_beans.logic.meeting_spec import get_meeting_datetime
from yelp_beans.logic.meeting_spec import get_users_from_spec
from yelp_beans.models import User


secrets = None
send_grid_client = None
SENDGRID_SENDER = None


def load_secrets():
    if secrets is not None:
        return
    global secrets, send_grid_client, SENDGRID_SENDER
    secrets = json.loads(open("client_secrets.json").read())
    # TODO (rkwills) switch to a yelp sendgrid account
    send_grid_client = SendGridAPIClient(apikey=secrets["SENDGRID_API_KEY"])
    SENDGRID_SENDER = secrets["SENDGRID_SENDER"]


def send_single_email(email, subject, template, template_arguments):
    """ Send an email using the SendGrid API
        Args:
            - email :string => the user's work email (ie username@company.com)
            - subject :string => the subject line for the email
            - template :string => the template file, corresponding to the email sent.
            - template_arguments :dictionary => keyword arguments to specify to render_template
        Returns:
            - SendGrid response
    """
    load_secrets()
    env = Environment(loader=PackageLoader('yelp_beans', 'templates/email_templates'))
    template = env.get_template(template)
    rendered_template = template.render(template_arguments)

    message = mail.Mail(
        from_email=mail.Email(SENDGRID_SENDER),
        subject=subject,
        to_email=mail.Email(email),
        content=Content("text/html", rendered_template)
    )

    return send_grid_client.client.mail.send.post(request_body=message.get())


def send_batch_initial_opt_in_email(users):
    """Sends the initial batch email to ask if people want to join Yelp-Beans"""
    for user in users:
        send_single_email(
            user.email,
            "Want to meet other employees through Yelp-Beans?",
            "welcome_email.html",
            {'first_name': user.first_name}
        )


def send_batch_weekly_opt_in_email(meeting_spec):
    """Sends an email for the week asking if members want a meeting"""
    create_url = 'https://yelp-beans.appspot.com/meeting_request/{}'.format(
        meeting_spec.key.urlsafe())
    logging.info('created url ' + create_url)

    users = get_users_from_spec(meeting_spec)
    users = [user for user in users if user]

    logging.info(len(users))
    logging.info(meeting_spec)
    meeting_datetime = get_meeting_datetime(meeting_spec)
    subscription = meeting_spec.meeting_subscription.get()
    logging.info(meeting_datetime.strftime('%I:%M %p %Z'))

    for user in users:
        if not user.terminated:
            logging.info(user)
            logging.info(meeting_datetime)
            send_single_email(
                user.email,
                "Want a yelp-beans meeting this week?",
                "weekly_opt_in_email.html",
                {
                    'first_name': user.first_name,
                    'office': subscription.office,
                    'location': subscription.location,
                    'meeting_day': meeting_datetime.strftime('%A'),
                    'meeting_time': meeting_datetime.strftime('%I:%M %p %Z'),
                    'meeting_url': create_url,
                    'link_to_change_pref': 'https://yelp-beans.appspot.com/'
                }
            )
            logging.info('sent email')
        else:
            logging.info(user)
            logging.info('terminated')


def send_batch_meeting_confirmation_email(matches, spec):
    """
    Sends an email to all of the participants in a match for the week
        matches - list of meetings to participants
        spec - meeting spec
    """
    for match in matches:
        participants = {participant.key for participant in match if isinstance(participant, User)}
        for participant in participants:
            others = participants - {participant}
            send_match_email(participant.get(), [participant.get() for participant in others], spec)


def send_match_email(user, participants, meeting_spec):
    """
    Sends an email to one of the matches for the week
        user - user receiving the email
        participants - other people in the meeting
        meeting_spec - meeting specification
    """
    meeting_datetime = get_meeting_datetime(meeting_spec)
    meeting_datetime_end = meeting_datetime + datetime.timedelta(minutes=30)
    subscription = meeting_spec.meeting_subscription.get()

    send_single_email(
        user.email,
        'Yelp Beans Meeting',
        'match_email.html',
        {
            'user': user,
            'participants': participants,
            'location': subscription.office + " " + subscription.location,
            'meeting_start_day': meeting_datetime.strftime('%A'),
            'meeting_start_date': meeting_datetime.strftime('%m/%d/%Y'),
            'meeting_start_time': meeting_datetime.strftime('%I:%M %p %Z'),
            'meeting_end_time': meeting_datetime_end.strftime('%I:%M %p %Z'),
            'calendar_invite_url': create_google_calendar_invitation_link(
                participants,
                subscription.title,
                subscription.office,
                subscription.location,
                meeting_datetime,
                meeting_datetime_end
            ),
        }
    )


def create_google_calendar_invitation_link(user_list, title, office, location, meeting_datetime, end_time):
    invite_url = "https://www.google.com/calendar/render?action=TEMPLATE&"
    url_params = {
        'text': "Meeting with {users} for {title}".format(
            users=', '.join([user.get_username() for user in user_list]),
            title=title
        ),
        # ToDo (xili|20161110) Fix the time zone issue for remote/HH
        'dates': "{begin_date}T{begin_time}/{end_date}T{end_time}".format(
            begin_date=meeting_datetime.strftime("%Y%m%d"),
            begin_time=meeting_datetime.strftime("%H%M%S"),
            end_date=end_time.strftime("%Y%m%d"),
            end_time=end_time.strftime("%H%M%S"),
        ),
        'details': "Yelp Beans Coffee time!",
        # ToDo (xili|20161110) Fix the location if one of the users is remote
        'location': office + " " + location,
    }
    invite_url += urllib.urlencode(url_params)
    return invite_url


def send_batch_unmatched_email(unmatched):
    """Sends an email to a person that couldn't be matched for the week"""
    for user in unmatched:
        user = user.key.get()
        send_single_email(
            user.email,
            'Your yelp-beans meeting this week',
            'unmatched_email.html',
            {'first_name': user.first_name}
        )
