# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import mock
import pytest
from yelp_beans.data_providers import json_file_data_provider


@pytest.fixture
def data_provider():
    return json_file_data_provider.JSONFileDataProvider(
        path=mock.sentinel.path,
    )


def test_fetch(data_provider, employees):
    with mock.patch.object(
        json_file_data_provider,
        'open',
        mock.mock_open(read_data=employees)
    ) as mock_open:
        result = data_provider._fetch(None)
        mock_open.assert_called_once_with(mock.sentinel.path, 'rb')
        assert len(result) == 1
