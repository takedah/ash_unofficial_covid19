from datetime import date

import pytest
import requests

from ash_unofficial_covid19.scrapers.tokyo_patients_number import ScrapeTokyoPatientsNumber


@pytest.fixture()
def csv_content():
    csv_content = """
全国地方公共団体コード,都道府県名,市区町村名,公表_年月日,日別陽性者数,7日間合計陽性者数,7日間平均陽性者数,日別判明者数,日別不明者数,7日間平均不明者数,7日間平均不明者増加比
130001,東京都,,2020-02-14,2,3,0.4,,,,
130001,東京都,,2020-02-15,8,11,1.6,,,,
130001,東京都,,2021-08-30,1969,26579,3797,824,1145,2224.9,0.769
"""
    return csv_content.encode("utf-8")


def test_lists(csv_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = csv_content
    responce_mock.headers = {"content-type": "text/csv"}
    mocker.patch.object(requests, "get", return_value=responce_mock)
    csv_data = ScrapeTokyoPatientsNumber("http://dummy.local")
    expect = [
        {
            "publication_date": date(2020, 2, 14),
            "patients_number": 2,
        },
        {
            "publication_date": date(2020, 2, 15),
            "patients_number": 8,
        },
        {
            "publication_date": date(2021, 8, 30),
            "patients_number": 1969,
        },
    ]
    assert csv_data.lists == expect
