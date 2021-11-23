import pandas as pd
import pytest
import requests

from ash_unofficial_covid19.scrapers.reservation_status import ScrapeReservationStatus


@pytest.fixture()
def pdf_dataframe():
    df1 = pd.DataFrame([[]])
    df2 = pd.DataFrame(
        [
            ["医療機関名", "予約受", "状況", "", "", "象者", "", "", ""],
            ["電話番号", "受付中 又は\r受付停止中", "接種可能時期", "年 齢", "かかりつけ", "かかりつけ\r以外", "その他", "", ""],
            [
                "市立旭川病院\r金星町１丁目\r29-0202 予約専用",
                "―",
                "―",
                "―",
                "―",
                "―",
                "―",
                "",
                "詳細は病院のホームページで確認してください。",
            ],
            [
                "独立行政法人\r国立病院機構旭川医療センター\r花咲町7\r51-3910",
                "受付中",
                "１０月１日〜火・木曜日午後",
                "指定なし",
                "※○",
                "―",
                "―",
                "",
                "予約専用",
            ],
        ]
    )
    return [df1, df2]


def test_lists(pdf_dataframe, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = "".encode("utf-8")
    responce_mock.headers = {"content-type": "application/pdf"}
    mocker.patch.object(requests, "get", return_value=responce_mock)
    mocker.patch.object(ScrapeReservationStatus, "_get_dataframe", return_value=pdf_dataframe)
    scraper = ScrapeReservationStatus("http://dummy.local")
    expect = [
        {
            "medical_institution_name": "市立旭川病院",
            "address": "金星町１丁目",
            "phone_number": "29-0202 予約専用",
            "status": "",
            "inoculation_time": "",
            "target_age": "",
            "target_family": False,
            "target_not_family": False,
            "target_suberbs": False,
            "target_other": "",
            "memo": "詳細は病院のホームページで確認してください。",
        },
        {
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7",
            "phone_number": "51-3910",
            "status": "受付中",
            "inoculation_time": "１０月１日〜火・木曜日午後",
            "target_age": "指定なし",
            "target_family": True,
            "target_not_family": False,
            "target_suberbs": False,
            "target_other": "",
            "memo": "※予約専用",
        },
    ]
    assert scraper.lists == expect


def test_get_name_list(pdf_dataframe, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = "".encode("utf-8")
    responce_mock.headers = {"content-type": "application/pdf"}
    mocker.patch.object(requests, "get", return_value=responce_mock)
    mocker.patch.object(ScrapeReservationStatus, "_get_dataframe", return_value=pdf_dataframe)
    scraper = ScrapeReservationStatus("http://dummy.local")
    expect = ["市立旭川病院", "独立行政法人国立病院機構旭川医療センター"]
    result = scraper.get_name_list()
    assert result == expect
