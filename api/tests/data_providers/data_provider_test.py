# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from yelp_beans.data_providers.data_provider import DataProvider


def test_parse(employees):
    result = DataProvider()._parse(json.loads(employees))
    assert len(result) == 1
    assert result[0]['first_name'] == 'Darwin'
    assert result[0]['last_name'] == 'Stoppelman'
    assert result[0]['email'] == 'darwin@googleapps.com'
    assert result[0]['photo_url'] == (
        "http://s3-media4.fl.yelpcdn.com/"
        "assets/srv0/yelp_large_assets/3f74899c069c/assets/img/"
        "illustrations/mascots/darwin@2x.png"
    )
    assert result[0]['metadata'] == {}
