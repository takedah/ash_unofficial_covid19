import unittest
from datetime import date
from unittest.mock import Mock, patch

from ash_unofficial_covid19.scrapers.downloader import DownloadedHTML
from ash_unofficial_covid19.scrapers.press_release_link import (
    ScrapePressReleaseLink
)


def html_content():
    return """
<p><a href="test.html">新型コロナウイルス感染症の発生状況（令和3年8月19日発表分）（PDF形式90キロバイト）</a></p>
"""


class TestScrapePressReleaseLink(unittest.TestCase):
    def setUp(self):
        self.html_content = html_content()

    def tearDown(self):
        pass

    @patch("ash_unofficial_covid19.scrapers.downloader.requests")
    def test_lists(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content
        )
        downloaded_html = DownloadedHTML("http://dummy.local/kurashi/")
        scraper = ScrapePressReleaseLink(
            downloaded_html=downloaded_html, target_year=2021
        )
        expect = [
            {
                "publication_date": date(2021, 8, 19),
                "url": "http://dummy.local/kurashi/test.html",
            },
        ]
        self.assertEqual(scraper.lists, expect)


if __name__ == "__main__":
    unittest.main()
