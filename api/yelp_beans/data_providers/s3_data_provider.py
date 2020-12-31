import json

import boto3
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
        ).Object(
            self.bucket_name,
            self.key
        )
        contents = bucket.get()['Body'].read().decode('utf-8')
        return json.loads(contents)

    def _obtain_s3_connection(self, access_key_id, secret_access_key):
        return boto3.resource(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )
