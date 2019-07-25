# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from yelp_beans.logic.data_ingestion import DataIngestion


def test_ingest():
    result = DataIngestion().ingest()
    assert len(result) == 1
