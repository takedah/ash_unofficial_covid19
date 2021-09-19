import unittest
from io import BytesIO
from unittest.mock import Mock, patch

import pandas as pd

from ash_unofficial_covid19.scrapers.reservation_status import (
    ScrapeReservationStatus
)


class TestScrapeReservationStatus(unittest.TestCase):
    @patch(
        "ash_unofficial_covid19.scrapers.reservation_status"
        + ".ScrapeReservationStatus.get_pdf"
    )
    @patch(
        "ash_unofficial_covid19.scrapers.reservation_status"
        + ".ScrapeReservationStatus._get_dataframe"
    )
    @patch("ash_unofficial_covid19.scrapers.downloader.requests")
    def test_lists(self, mock_requests, mock_get_dataframe, mock_get_pdf):
        mock_requests.get.return_value = Mock(
            status_code=200,
            content="".encode("utf-8"),
            headers={"content-type": "application/pdf"},
        )
        dfs = list()
        df1 = pd.DataFrame([[]])
        df2 = pd.DataFrame(
            [
                [
                    "医療機関名",
                    "住　　所",
                    "電話番号",
                    "予約受付状況又は受付開始時間",
                    "対　象　者",
                    "摂取期間・時期",
                    "備　　　考",
                ],
                [
                    "市立旭川病院",
                    "金星町１丁目",
                    "29-0202\r予約専用",
                    "―",
                    "―",
                    "―",
                    "詳細は病院のホームページで確認してください。",
                ],
            ]
        )
        dfs = [df1, df2]
        mock_get_dataframe.return_value = dfs
        mock_get_pdf.return_value = BytesIO()
        dummy_url = "http://dummy.local"
        scraper = ScrapeReservationStatus(dummy_url)
        expect = [
            {
                "medical_institution_name": "市立旭川病院",
                "address": "金星町１丁目",
                "phone_number": "29-0202 予約専用",
                "status": "―",
                "target": "―",
                "inoculation_time": "―",
                "memo": "詳細は病院のホームページで確認してください。",
            },
        ]
        self.assertEqual(scraper.lists, expect)


if __name__ == "__main__":
    unittest.main()
