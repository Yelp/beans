# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.data_providers.workday import get_json_employee_data


def test_workday():
    employees = get_json_employee_data()
    actual_fields = set(employees[0].keys())

    expected_fields = set([
        'email',
        'first_name',
        'last_name',
        'photo_url',
        'metadata',
    ])

    assert actual_fields == expected_fields

    assert employees[0]['metadata']
