# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import os

from flask import Flask
from flask import render_template

from yelp_beans.routes.api.v1.meeting_requests import meeting_requests
from yelp_beans.routes.api.v1.metrics import metrics_blueprint
from yelp_beans.routes.api.v1.preferences import preferences_blueprint
from yelp_beans.routes.api.v1.user import user_blueprint
from yelp_beans.routes.tasks import tasks

app = Flask(__name__, template_folder='yelp_beans/templates')


# React endpoints
@app.route('/dashboard')
def dashboard_page():
    return render_template('admin_pages.html')


@app.route('/')
def main_page():
    return render_template('user_pages.html')


@app.route('/user/<email>')
def main_page_user(email):
    return render_template('user_pages.html')


@app.route('/meeting_request/<id>')
def meeting_request(id):
    return render_template('user_pages.html')


# Cron Endpoint
app.register_blueprint(tasks, url_prefix='/tasks')

# Api Endpoints
app.register_blueprint(meeting_requests, url_prefix='/v1/meeting_request')
app.register_blueprint(metrics_blueprint, url_prefix='/v1/metrics')
app.register_blueprint(preferences_blueprint, url_prefix='/v1/user/preferences')
app.register_blueprint(user_blueprint, url_prefix='/v1/user')


if 'Development' in os.environ.get('SERVER_SOFTWARE', ''):
    from tests.conftest import create_dev_data
    create_dev_data()
