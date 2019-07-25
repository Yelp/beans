# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from boto import connect_s3
from boto.s3.key import Key
from yelp_beans.data_providers.data_provider import DataProvider


class S3DataProvider(DataProvider):

    def __init__(
        self,
        access_key_id=None,
        secret_access_key=None,
        bucket_name=None,
        key=None
    ):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = bucket_name
        self.key = key

    def _fetch(self, data):
        bucket = self._obtain_s3_connection(
            self.access_key_id,
            self.secret_access_key,
        ).get_bucket(
            self.bucket_name,
        )
        contents = Key(bucket, self.key).get_contents_as_string()
        return json.loads(contents)

    def _obtain_s3_connection(self, access_key_id, secret_access_key):
        return connect_s3(
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
