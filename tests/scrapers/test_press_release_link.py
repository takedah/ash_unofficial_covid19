from datetime import date

import pytest
import requests

from ash_unofficial_covid19.errors import ScrapeError
from ash_unofficial_covid19.scrapers.press_release_link import ScrapePressReleaseLink


@pytest.fixture()
def html_content():
    return """
<p><a href="test.html">新型コロナウイルス感染症の発生状況（令和3年8月19日発表分）（PDF形式90キロバイト）</a></p>
"""


def test_lists(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    dummy_url = "http://dummy.local/kurashi/test.html"
    scraper = ScrapePressReleaseLink(html_url=dummy_url, target_year=2021)
    expect = [
        {
            "publication_date": date(2021, 8, 19),
            "url": dummy_url,
        },
    ]
    assert scraper.lists == expect


def test_target_year_error(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    with pytest.raises(ScrapeError, match="対象年の指定が正しくありません。"):
        ScrapePressReleaseLink(html_url="http://dummy.local", target_year=2019)
