from datetime import date

import pandas as pd
import pytest
import requests

from ash_unofficial_covid19.scrapers.patients_number import ScrapePatientsNumber


class TestScrapePatientsNumber:
    @pytest.fixture()
    def pdf_dataframes(self):
        df1 = pd.DataFrame(
            [
                ["確認数\n番　　号"],
                ["4419例目～4515例目（道内81535例目～81631例目）\n1月27日確認分\n97\n人"],
                ["うち再陽性者数　0人"],
            ]
        )
        df2 = pd.DataFrame(
            [
                ["旭川市", 96],
                ["旭川市外（道内）", 1],
                ["旭川市外（道外）", 0],
            ]
        )
        df3 = pd.DataFrame(
            [
                ["無症状", 3],
                ["軽症", 53],
                ["中等症", 0],
                ["重症", 0],
                ["調査中", 41],
            ]
        )
        df4 = pd.DataFrame(
            [
                ["10歳未満", 12],
                ["10歳代", 19],
                ["20歳代", 12],
                ["30歳代", 14],
                ["40歳代", 13],
                ["50歳代", 15],
                ["60歳代", 3],
                ["70歳代", 2],
                ["80歳代", 2],
                ["90歳以上", 0],
                ["調査中", 5],
            ]
        )
        return [df1, df2, df3, df4]

    def test_lists(self, pdf_dataframes, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = "".encode("utf-8")
        responce_mock.headers = {"content-type": "application/pdf"}
        mocker.patch.object(requests, "get", return_value=responce_mock)
        mocker.patch.object(ScrapePatientsNumber, "_get_dataframes", return_value=pdf_dataframes)
        scraper = ScrapePatientsNumber(pdf_url="http://dummy.local", publication_date=date(2022, 1, 28))
        expect = [
            {
                "publication_date": date(2022, 1, 28),
                "age_under_10": 12,
                "age_10s": 19,
                "age_20s": 12,
                "age_30s": 14,
                "age_40s": 13,
                "age_50s": 15,
                "age_60s": 3,
                "age_70s": 2,
                "age_80s": 2,
                "age_over_90": 0,
                "investigating": 5,
            },
        ]
        assert scraper.lists == expect
