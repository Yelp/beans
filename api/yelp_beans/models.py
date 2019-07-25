# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from google.appengine.ext import ndb


class User(ndb.Model):
    """ Models a Yelp employee.
        Schema:
        - email:            gmail email
        - first_name:       self-explanatory
        - last_name:        self-explanatory
        - photo_url:        url to user photo
        - terminated:       TRUE when user has left the company
    """
    email = ndb.StringProperty()
    first_name = ndb.StringProperty(indexed=False)
    last_name = ndb.StringProperty(indexed=False)
    photo_url = ndb.TextProperty()
    metadata = ndb.JsonProperty()
    terminated = ndb.BooleanProperty(default=False, required=True)
    subscription_preferences = ndb.KeyProperty(
        kind="UserSubscriptionPreferences",
        repeated=True
    )

    def get_username(self):
        return self.email.split('@')[0]


class MeetingSubscription(ndb.Model):
    """ The base template for a meeting type, it is comprised of
        weekly Meeting days and times that are recurring
        Schema:
            - title:            name of the meeting
            - datetime:         datetimes available for the meeting subscription
            - location:         location of the meetings
            - size:             size of the meetings
            - user_list:        users requested/ have access to join subscription
            - user_rules:       rules set for allowing people to see a subscription
            - dept_rules:       rules set for matching people
    """
    title = ndb.StringProperty()
    datetime = ndb.KeyProperty(kind="SubscriptionDateTime", repeated=True)
    size = ndb.IntegerProperty()
    office = ndb.StringProperty()
    location = ndb.StringProperty()
    timezone = ndb.StringProperty()
    user_list = ndb.KeyProperty(kind="User", repeated=True)
    user_rules = ndb.KeyProperty(kind="Rule", repeated=True)
    dept_rules = ndb.KeyProperty(kind="Rule", repeated=True)
    rule_logic = ndb.StringProperty()


class Rule(ndb.Model):
    """
    Define dynamic rules in which we want to filter who belongs to what subscription list
    """
    name = ndb.StringProperty()
    value = ndb.StringProperty()


class UserSubscriptionPreferences(ndb.Model):
    """ User's time preferences for a given meeting subscription.
        Schema:
            - subscription:               subscription the employee is subscribed to
            - preference:                 time the employee prefers to meet
    """
    subscription = ndb.KeyProperty(kind="MeetingSubscription")
    preference = ndb.KeyProperty(kind="SubscriptionDateTime")


class SubscriptionDateTime(ndb.Model):
    """ A datetime object used to normalize datetimes in different entities
        Schema:
            - datetime:                 shared time value
    """
    datetime = ndb.DateTimeProperty()


class MeetingSpec(ndb.Model):
    """ A instance of a meeting for a specific week.
        Schema:
            - datetime:                 the time that the meeting will take place
            - meeting_subscription:     the meeting subscription the spec is attached to
    """
    datetime = ndb.DateTimeProperty()
    meeting_subscription = ndb.KeyProperty(kind="MeetingSubscription")


class MeetingRequest(ndb.Model):
    """ Represents a user's meeting intent, essentially:
        User: "I want to meet with someone this week."
        Schema:
            - user:             References a User item
            - meeting_spec:     References a MeetingSpec item, a grouping that
                                represents all users who want to meet together.
    """
    user = ndb.KeyProperty(kind="User")
    meeting_spec = ndb.KeyProperty(kind="MeetingSpec")


class Meeting(ndb.Model):
    """ Models a single meeting.
        Schema:
            - cancelled:    TRUE if meeting is cancelled
            - meeting_spec: meta data representing a
                grouping of meetings
    """
    meeting_spec = ndb.KeyProperty(kind="MeetingSpec")
    cancelled = ndb.BooleanProperty(default=False)


class MeetingParticipant(ndb.Model):
    """ Records a tuple of (Meeting, User).
        Schema:
            - meeting:              References a Meeting item.
            - user:                 References a User item.
    """
    meeting = ndb.KeyProperty(kind="Meeting")
    user = ndb.KeyProperty(kind="User")
