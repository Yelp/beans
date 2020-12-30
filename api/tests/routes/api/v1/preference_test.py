import json

from yelp_beans.routes.api.v1 import preferences
from yelp_beans.routes.api.v1.preferences import preferences_api
from yelp_beans.routes.api.v1.preferences import preferences_api_post


def test_preferences_api_no_user(app, session):
    with app.test_request_context('/?email=darwin@yelp.com'):
        response = preferences_api()
    assert response.json == []


def test_preferences_api_user_exists(app, database, fake_user):
    with app.test_request_context('/?email=darwin@yelp.com'):
        response = preferences_api().json
    assert response == [
        {
            'id': database.sub.id,
            'title': 'Yelp Weekly',
            'location': '8th Floor',
            'office': 'USA: CA SF New Montgomery Office',
            'timezone': 'America/Los_Angeles',
            'size': 2,
            'rule_logic': None,
            'datetime': [
                {
                    'active': True,
                    'date': '2017-01-20T23:00:00+00:00',
                    'id': database.sub.datetime[0].id
                },
                {
                    'active': False,
                    'date': '2017-01-20T19:00:00+00:00',
                    'id': database.sub.datetime[1].id
                }
            ],
        }
    ]


def test_preference_api_post(monkeypatch, app, database, fake_user):
    monkeypatch.setattr(
        preferences,
        'get_user',
        lambda x: fake_user
    )
    sub_key = database.sub.id
    assert fake_user.subscription_preferences != []
    with app.test_request_context(
            '/v1/user/preferences/subscription/{}'.format(sub_key),
            method='POST',
            data=json.dumps({
                database.sub.datetime[0].id: False,
                'email': fake_user.email,
            }),
            content_type='application/json'
    ):
        response = preferences_api_post(sub_key)

    assert response == 'OK'
    assert fake_user.subscription_preferences == []
