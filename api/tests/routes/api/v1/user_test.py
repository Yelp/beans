# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.routes.api.v1.user import user_api


def test_get_user(app, database, fake_user):
    with app.test_request_context('/?email=darwin@yelp.com'):
        response = user_api().json
    assert {
        'first_name': fake_user.first_name,
        'last_name': fake_user.last_name,
        'photo_url': fake_user.photo_url,
        'metadata': fake_user.metadata
    } == response


def test_get_user_none(app, minimal_database):
    with app.test_request_context('/?email=test_user'):
        response = user_api().json
    assert {} == response
