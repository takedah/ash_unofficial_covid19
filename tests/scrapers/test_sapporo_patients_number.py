import unittest
from datetime import date
from unittest.mock import Mock, patch

from ash_unofficial_covid19.scrapers.sapporo_patients_number import (
    ScrapeSapporoPatientsNumber
)


def csv_content():
    csv_data = """
日付,小計
2020-02-14T08:00:00.000Z,1
2020-02-15T08:00:00.000Z,0
2021-08-30T08:00:00.000Z,134
"""
    return csv_data.encode("utf-8")


class TestScrapeSapporoPatientsNumber(unittest.TestCase):
    def setUp(self):
        self.csv_content = csv_content()

    def tearDown(self):
        pass

    @patch("ash_unofficial_covid19.scrapers.downloader.requests")
    def test_lists(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200,
            content=csv_content(),
            headers={"content-type": "text/csv"},
        )
        dummy_url = "http://dummy.local"
        csv_data = ScrapeSapporoPatientsNumber(dummy_url)
        result = csv_data.lists
        expect = [
            {
                "publication_date": date(2020, 2, 13),
                "patients_number": 1,
            },
            {
                "publication_date": date(2020, 2, 14),
                "patients_number": 0,
            },
            {
                "publication_date": date(2021, 8, 29),
                "patients_number": 134,
            },
        ]
        self.assertEqual(result, expect)


if __name__ == "__main__":
    unittest.main()
