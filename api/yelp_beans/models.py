from database import db


class User(db.Model):
    """Models a Yelp employee.
        Schema:
        - email:            gmail email
        - first_name:       self-explanatory
        - last_name:        self-explanatory
        - photo_url:        url to user photo
        - terminated:       TRUE when user has left the company

    Unfortunately, metadata is an attribute already used by sqlalchemy so we use meta_data in
    the table. Note, however, that the json from the frontend uses metadata for the same column.
    """

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, index=True)
    first_name = db.Column(db.String())
    last_name = db.Column(db.String())
    photo_url = db.Column(db.Text)
    meta_data = db.Column(db.JSON)
    terminated = db.Column(db.Boolean, nullable=False, default=False)
    subscription_preferences = db.relationship("UserSubscriptionPreferences")

    def get_username(self):
        return self.email.split("@")[0]


class MeetingSubscription(db.Model):
    """The base template for a meeting type, it is comprised of
    weekly Meeting days and times that are recurring
    Schema:
        - title:                    name of the meeting
        - datetime:                 datetimes available for the meeting subscription
        - location:                 location of the meetings
        - size:                     size of the meetings
        - user_list:                users requested/ have access to join subscription
        - user_rules:               rules set for allowing people to see a subscription
        - dept_rules:               rules set for matching people
        - default_auto_opt_in:      boolean representing whether auto opt in for meeting requests is enabled
    """

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    datetime = db.relationship("SubscriptionDateTime", backref="meeting_subscription")
    size = db.Column(db.Integer)
    office = db.Column(db.String())
    location = db.Column(db.String())
    timezone = db.Column(db.String())
    rule_logic = db.Column(db.String())
    default_auto_opt_in = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user_list = db.relationship("User")
    user_rules = db.relationship("Rule", foreign_keys="Rule.user_subscription_id")
    dept_rules = db.relationship("Rule", foreign_keys="Rule.dept_subscription_id")


class Rule(db.Model):
    """
    Define dynamic rules in which we want to filter who belongs to what subscription list
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    value = db.Column(db.String())
    user_subscription_id = db.Column(db.Integer, db.ForeignKey("meeting_subscription.id"))
    dept_subscription_id = db.Column(db.Integer, db.ForeignKey("meeting_subscription.id"))


class UserSubscriptionPreferences(db.Model):
    """User's time preferences for a given meeting subscription.
    Schema:
        - subscription:               subscription the employee is subscribed to
        - preference:                 time the employee prefers to meet
        - auto_opt_in:                boolean representing whether auto opt in for meeting requests is enabled
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User")
    subscription_id = db.Column(db.Integer, db.ForeignKey("meeting_subscription.id"))
    subscription = db.relationship("MeetingSubscription", backref=db.backref("user_subscription_preferences", uselist=False))
    preference_id = db.Column(db.Integer, db.ForeignKey("subscription_date_time.id"))
    preference = db.relationship("SubscriptionDateTime", backref="user_subscription_preferences")
    auto_opt_in = db.Column(db.Boolean, default=db.ForeignKey("meeting_subscription.default_auto_opt_in"))


class SubscriptionDateTime(db.Model):
    """A datetime object used to normalize datetimes in different entities
    Schema:
        - datetime:                 shared time value
    """

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    meeting_subscription_id = db.Column(db.Integer, db.ForeignKey("meeting_subscription.id"))


class MeetingSpec(db.Model):
    """A instance of a meeting for a specific week.
    Schema:
        - datetime:                 the time that the meeting will take place
        - meeting_subscription:     the meeting subscription the spec is attached to
    """

    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime)
    meeting_subscription_id = db.Column(db.Integer, db.ForeignKey("meeting_subscription.id"))
    meeting_subscription = db.relationship("MeetingSubscription")


class MeetingRequest(db.Model):
    """Represents a user's meeting intent, essentially:
    User: "I want to meet with someone this week."
    Schema:
        - user:             References a User item
        - meeting_spec:     References a MeetingSpec item, a grouping that
                            represents all users who want to meet together.
    """

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User")
    meeting_spec_id = db.Column(db.Integer, db.ForeignKey("meeting_spec.id"))
    meeting_spec = db.relationship("MeetingSpec")


class Meeting(db.Model):
    """Models a single meeting.
    Schema:
        - cancelled:    TRUE if meeting is cancelled
        - meeting_spec: meta data representing a
            grouping of meetings
    """

    id = db.Column(db.Integer, primary_key=True)
    meeting_spec_id = db.Column(db.Integer, db.ForeignKey("meeting_spec.id"))
    meeting_spec = db.relationship("MeetingSpec")
    cancelled = db.Column(db.Boolean, nullable=False, default=False)


class MeetingParticipant(db.Model):
    """Records a tuple of (Meeting, User).
    Schema:
        - meeting:              References a Meeting item.
        - user:                 References a User item.
    """

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey("meeting.id"), nullable=False)
    meeting = db.relationship("Meeting")
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")
