# -*- coding: utf-8 -*-
from yelp_beans.logic.data_ingestion import DataIngestion


def test_ingest():
    result = DataIngestion().ingest()
    assert len(result) == 1
