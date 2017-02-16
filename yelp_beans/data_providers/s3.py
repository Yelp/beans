# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from boto import connect_s3
from boto.s3.key import Key

from yelp_beans.data_providers.data_provider import DataProvider


class S3Provider(DataProvider):

    secrets = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
    ]

    def fetch(self, access_key_id, secret_access_key):
        bucket = self.obtain_s3_connection(
            access_key_id,
            secret_access_key,
        ).get_bucket(
            self.bucket_name(),
        )
        contents = Key(bucket, self.key_name()).get_contents_as_string()
        return json.loads(contents)

    def obtain_s3_connection(self, access_key_id, secret_access_key):
        return connect_s3(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )


class PhotosProvider(S3Provider):

    def bucket_name(self):
        return 'yelp-employees'

    def key_name(self):
        return 'employees.json'

    def munge(self, old_data):
        new_data = {}
        for data in old_data:
            photo_url = data['photos'].get(
                'ls',
                (
                    'http://s3-media4.fl.yelpcdn.com'
                    '/assets/srv0/yelp_large_assets/3f74899c069c/'
                    'assets/img/illustrations/mascots/darwin@2x.png'
                ),
            )
            if photo_url:
                photo_url.replace('http', 'https')

            new_data[data['email']]['photo_url'] = photo_url
            user_id = data.get('user_id', '')
            company_profile_url = '' if not user_id else 'https://www.yelp.com/user_details?userid={}'.format(user_id)
            new_data[data['email']]['company_profile_url'] = company_profile_url

        return new_data


def get_json_employee_data_from_s3():
    """
    Returns: list of dictionaries of employees
    """
    provider = PhotosProvider()
    return provider()
