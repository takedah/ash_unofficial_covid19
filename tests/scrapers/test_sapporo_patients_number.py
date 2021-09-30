from datetime import date

import pytest
import requests

from ash_unofficial_covid19.scrapers.sapporo_patients_number import ScrapeSapporoPatientsNumber


@pytest.fixture()
def csv_content():
    csv_content = """
日付,小計
2020-02-14T08:00:00.000Z,1
2020-02-15T08:00:00.000Z,0
2021-08-30T08:00:00.000Z,134
"""
    return csv_content.encode("utf-8")


def test_lists(csv_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = csv_content
    responce_mock.headers = {"content-type": "text/csv"}
    mocker.patch.object(requests, "get", return_value=responce_mock)
    csv_data = ScrapeSapporoPatientsNumber("http://dummy.local")
    expect = [
        {
            "publication_date": date(2020, 2, 14),
            "patients_number": 1,
        },
        {
            "publication_date": date(2020, 2, 15),
            "patients_number": 0,
        },
        {
            "publication_date": date(2021, 8, 30),
            "patients_number": 134,
        },
    ]
    assert csv_data.lists == expect
