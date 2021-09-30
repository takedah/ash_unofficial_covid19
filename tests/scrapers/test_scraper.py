from datetime import date

import pytest
import requests

from ash_unofficial_covid19.scrapers.downloader import (
    DownloadedCSV,
    DownloadedHTML,
    DownloadedJSON,
    DownloadedPDF,
)
from ash_unofficial_covid19.scrapers.scraper import Scraper


def test_get_html(mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = ""
    mocker.patch.object(requests, "get", return_value=responce_mock)
    html_file = DownloadedHTML("http://dummy.local")
    assert isinstance(html_file, DownloadedHTML)


def test_get_csv(mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = "".encode("utf-8")
    responce_mock.headers = {"content-type": "text/csv"}
    mocker.patch.object(requests, "get", return_value=responce_mock)
    csv_file = DownloadedCSV(url="http://dummy.local")
    assert isinstance(csv_file, DownloadedCSV)


def test_get_pdf(mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = "".encode("utf-8")
    mocker.patch.object(requests, "get", return_value=responce_mock)
    pdf_file = DownloadedPDF("http://dummy.local")
    assert isinstance(pdf_file, DownloadedPDF)


def test_get_json(mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = '{"test": "test"}'
    mocker.patch.object(requests, "get", return_value=responce_mock)
    json_file = DownloadedJSON("http://dummy.local")
    assert isinstance(json_file, DownloadedJSON)


@pytest.mark.parametrize(
    "value,expected",
    [
        ("3月6日", date(2021, 3, 6)),
        ("３月６日", date(2021, 3, 6)),
        ("13月6日", None),
    ],
)
def test_format_date(value, expected):
    assert Scraper.format_date(date_string=value, target_year=2021) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("３月６日", "3月6日"),
        ("3月6日", "3月6日"),
        (36, ""),
    ],
)
def test_z2h_number(value, expected):
    assert Scraper.z2h_number(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("20代", "20代"),
        ("調査中", ""),
        ("10代未満", "10歳未満"),
        ("100代", "90歳以上"),
    ],
)
def test_format_age(value, expected):
    assert Scraper.format_age(value) == expected


@pytest.mark.parametrize(
    "value,expected",
    [
        ("男性", "男性"),
        ("非公表", ""),
        ("その他", "その他"),
        ("women", ""),
    ],
)
def test_format_sex(value, expected):
    assert Scraper.format_sex(value) == expected
