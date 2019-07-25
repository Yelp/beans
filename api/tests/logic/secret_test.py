# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

import pytest
from yelp_beans.logic.secret import get_secret


def test_get_secret_file(tmpdir, database):
    with tmpdir.as_cwd():
        expected = 'password'
        with open(tmpdir.join('client_secrets.json').strpath, 'w') as secrets:
            secret = {'secret': expected}
            secrets.write(json.dumps(secret))
        actual = get_secret('secret')
        assert expected == actual


def test_get_secret_file_no_exist(tmpdir, database):
    with tmpdir.as_cwd():
        with pytest.raises(IOError):
            assert get_secret('secret')
