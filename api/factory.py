# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from database import db
from flask import Flask


def create_app():
    app = Flask(__name__, template_folder='yelp_beans/templates')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    db.init_app(app)

    from yelp_beans.routes.api.v1.meeting_requests import meeting_requests
    from yelp_beans.routes.api.v1.metrics import metrics_blueprint
    from yelp_beans.routes.api.v1.preferences import preferences_blueprint
    from yelp_beans.routes.api.v1.user import user_blueprint
    from yelp_beans.routes.tasks import tasks
    # Cron Endpoint
    app.register_blueprint(tasks, url_prefix='/tasks')

    # Api Endpoints
    app.register_blueprint(meeting_requests, url_prefix='/v1/meeting_request')
    app.register_blueprint(metrics_blueprint, url_prefix='/v1/metrics')
    app.register_blueprint(preferences_blueprint,
                           url_prefix='/v1/user/preferences')
    app.register_blueprint(user_blueprint, url_prefix='/v1/user')

    with app.app_context():
        db.create_all()

    return app
