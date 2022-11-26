from datetime import date, datetime, timezone

import pytest

from ash_unofficial_covid19.models.child_reservation_status import ChildReservationStatusFactory
from ash_unofficial_covid19.models.first_reservation_status import FirstReservationStatusFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.child_reservation_status import ChildReservationStatusService
from ash_unofficial_covid19.services.first_reservation_status import FirstReservationStatusService
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.services.press_release_link import PressReleaseLinkService
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService
from ash_unofficial_covid19.views.xml import AtomView, RssView


@pytest.fixture()
def setup():
    # 追加接種（オミクロン対応ワクチン）予約受付状況のセットアップ
    test_data = [
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "target_age": "",
            "is_target_family": False,
            "is_target_not_family": False,
            "target_other": "当院の患者IDをお持ちの方",
            "memo": "当院ホームページをご確認ください",
        },
        {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "vaccine": "ファイザー モデルナ",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "target_age": "18歳以上",
            "is_target_family": True,
            "is_target_not_family": False,
            "target_other": "",
            "memo": "",
        },
    ]
    factory = ReservationStatusFactory()
    for row in test_data:
        factory.create(**row)

    service = ReservationStatusService()
    service.create(factory)

    # 1・2回目予約受付状況のセットアップ
    test_data = [
        {
            "area": "新富・東・金星町地区",
            "medical_institution_name": "市立旭川病院",
            "address": "金星町1丁目",
            "phone_number": "29-0202予約専用",
            "vaccine": None,
            "status": "",
            "inoculation_time": "",
            "target_age": "",
            "is_target_family": None,
            "is_target_not_family": None,
            "is_target_suberb": None,
            "target_other": "",
            "memo": "",
        },
        {
            "area": "各条１７～２６丁目・宮前・南地区",
            "medical_institution_name": "森山病院",
            "address": "宮前2条1丁目",
            "phone_number": "45-2026予約専用",
            "vaccine": None,
            "status": "受付中",
            "inoculation_time": "2月28日～8月",
            "target_age": "18歳以上",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": True,
            "target_other": "",
            "memo": "月・水 14:00～15:00",
        },
    ]
    factory = FirstReservationStatusFactory()
    for row in test_data:
        factory.create(**row)

    service = FirstReservationStatusService()
    service.create(factory)

    # 5～11歳予約受付状況のセットアップ
    test_data = [
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "vaccine": "",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "target_age": "",
            "is_target_family": False,
            "is_target_not_family": False,
            "target_other": "当院の患者IDをお持ちの方",
            "memo": "当院ホームページをご確認ください",
        },
        {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "vaccine": "",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "target_age": "18歳以上",
            "is_target_family": True,
            "is_target_not_family": False,
            "target_other": "",
            "memo": "",
        },
    ]
    factory = ChildReservationStatusFactory()
    for row in test_data:
        factory.create(**row)

    service = ChildReservationStatusService()
    service.create(factory)


class TestRssView:
    def test_get_feed(self, setup, mocker):
        aggregate_by_days = [
            (date(2022, 1, 21), 0),
            (date(2022, 1, 22), 0),
            (date(2022, 1, 23), 0),
            (date(2022, 1, 24), 0),
            (date(2022, 1, 25), 0),
            (date(2022, 1, 26), 0),
            (date(2022, 1, 28), 97),
            (date(2022, 1, 29), 102),
        ]
        per_hundred_thousand_population_per_week = [
            (date(2022, 1, 20), 0),
            (date(2022, 1, 27), 60.05),
        ]
        mocker.patch.object(PatientsNumberService, "get_aggregate_by_days", return_value=aggregate_by_days)
        mocker.patch.object(
            PatientsNumberService,
            "get_per_hundred_thousand_population_per_week",
            return_value=per_hundred_thousand_population_per_week,
        )
        mocker.patch.object(PressReleaseLinkService, "get_latest_publication_date", return_value=date(2022, 1, 29))
        mocker.patch.object(
            ReservationStatusService, "get_last_updated", return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc)
        )
        mocker.patch.object(
            FirstReservationStatusService,
            "get_last_updated",
            return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc),
        )
        mocker.patch.object(
            ChildReservationStatusService,
            "get_last_updated",
            return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc),
        )
        rss = RssView(date(2022, 1, 29))
        expect = {
            "title": "旭川市新型コロナウイルスまとめサイト",
            "link": "https://covid19.asahikawa-opendata.morori.jp/",
            "description": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
            + "また、旭川市の新型コロナワクチン接種医療機関の情報を、地図から探すことができる旭川市コロナワクチンマップも公開していますので、"
            + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
            "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
            "last_build_date": "Sat, 29 Jan 2022 07:00:00 GMT",
            "rss_url": "https://covid19.asahikawa-opendata.morori.jp/rss.xml",
            "items": [
                {
                    "description": "2022/01/29 (Sat) の旭川市の新型コロナ新規感染者数は102人で、先週の同じ曜日から+102人でした。"
                    + "直近1週間の人口10万人あたりの新規感染者数は60.05人で、先週から+60.05人となっています。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/",
                    "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
                    "title": "2022/01/29 (Sat) の旭川市内感染状況の最新動向",
                },
                {
                    "description": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
                    + "また、旭川市の新型コロナワクチン接種医療機関の情報を、地図から探すことができる旭川市コロナワクチンマップも公開していますので、"
                    + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-02-27:/about",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/about",
                    "pub_date": "Sun, 27 Feb 2022 00:00:00 GMT",
                    "title": "旭川市新型コロナウイルスまとめサイトについて",
                },
                {
                    "description": "旭川市の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の予約受付状況などの情報を、地図から探すことができます。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_statuses",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市のコロナワクチンマップ（追加接種（オミクロン対応ワクチン））",
                },
                {
                    "description": "旭川市の新型コロナワクチン接種医療機関（1・2回目接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/first_reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_statuses",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市のコロナワクチンマップ（1・2回目接種）",
                },
                {
                    "description": "旭川市の新型コロナワクチン接種医療機関（5～11歳接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/child_reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_statuses",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市のコロナワクチンマップ（5～11歳接種）",
                },
                {
                    "description": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/opendata",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/opendata",
                    "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "description": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果",
                },
                {
                    "description": "西地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "西地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果",
                },
                {
                    "description": "各条１７～２６丁目・宮前・南地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E5%90%84%E6%9D%A1%EF%BC%91%EF%BC%97%EF%BD%9E%EF%BC%92%EF%BC%96%"
                    + "E4%B8%81%E7%9B%AE%E3%83%BB%E5%AE%AE%E5%89%8D%E3%83%BB%E5%8D%97%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E5%90%84%E6%9D%A1%EF%BC%91%EF%BC%97%EF%BD%9E%EF%BC%92%EF%BC%96%"
                    + "E4%B8%81%E7%9B%AE%E3%83%BB%E5%AE%AE%E5%89%8D%E3%83%BB%E5%8D%97%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "各条１７～２６丁目・宮前・南地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果",
                },
                {
                    "description": "新富・東・金星町地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E6%96%B0%E5%AF%8C%E3%83%BB%E6%9D%B1%E3%83%BB%E9%87%91%E6%98%9F%E7%94%BA%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E6%96%B0%E5%AF%8C%E3%83%BB%E6%9D%B1%E3%83%BB%E9%87%91%E6%98%9F%E7%94%BA%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "新富・東・金星町地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果",
                },
                {
                    "description": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果",
                },
                {
                    "description": "西地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "西地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果",
                },
                {
                    "description": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））",
                },
                {
                    "description": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））",
                },
                {
                    "description": "市立旭川病院の新型コロナワクチン接種予約受付状況（1・2回目接種）です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "市立旭川病院の新型コロナワクチン接種予約受付状況（1・2回目接種）",
                },
                {
                    "description": "森山病院の新型コロナワクチン接種予約受付状況（1・2回目接種）です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E6%A3%AE%E5%B1%B1%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E6%A3%AE%E5%B1%B1%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "森山病院の新型コロナワクチン接種予約受付状況（1・2回目接種）",
                },
                {
                    "description": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（5～11歳接種）です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（5～11歳接種）",
                },
                {
                    "description": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（5～11歳接種）です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（5～11歳接種）",
                },
            ],
        }
        result = rss.get_feed()
        assert result == expect


class TestAtomView:
    def test_get_feed(self, setup, mocker):
        aggregate_by_days = [
            (date(2022, 1, 21), 0),
            (date(2022, 1, 22), 0),
            (date(2022, 1, 23), 0),
            (date(2022, 1, 24), 0),
            (date(2022, 1, 25), 0),
            (date(2022, 1, 26), 0),
            (date(2022, 1, 28), 97),
            (date(2022, 1, 29), 102),
        ]
        per_hundred_thousand_population_per_week = [
            (date(2022, 1, 20), 0),
            (date(2022, 1, 27), 60.05),
        ]
        mocker.patch.object(PatientsNumberService, "get_aggregate_by_days", return_value=aggregate_by_days)
        mocker.patch.object(
            PatientsNumberService,
            "get_per_hundred_thousand_population_per_week",
            return_value=per_hundred_thousand_population_per_week,
        )
        mocker.patch.object(PressReleaseLinkService, "get_latest_publication_date", return_value=date(2022, 1, 29))
        mocker.patch.object(
            ReservationStatusService, "get_last_updated", return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc)
        )
        mocker.patch.object(
            FirstReservationStatusService,
            "get_last_updated",
            return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc),
        )
        mocker.patch.object(
            ChildReservationStatusService,
            "get_last_updated",
            return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc),
        )
        atom = AtomView(date(2022, 1, 29))
        expect = {
            "id": "https://covid19.asahikawa-opendata.morori.jp/",
            "title": "旭川市新型コロナウイルスまとめサイト",
            "atom_url": "https://covid19.asahikawa-opendata.morori.jp/atom.xml",
            "author": {
                "name": "takedah",
                "url": "https://github.com/takedah/ash_unofficial_covid19",
            },
            "updated": "2022-01-29T07:00:00Z",
            "entries": [
                {
                    "summary": "2022/01/29 (Sat) の旭川市の新型コロナ新規感染者数は102人で、先週の同じ曜日から+102人でした。"
                    + "直近1週間の人口10万人あたりの新規感染者数は60.05人で、先週から+60.05人となっています。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/",
                    "updated": "2022-01-29T07:00:00Z",
                    "title": "2022/01/29 (Sat) の旭川市内感染状況の最新動向",
                },
                {
                    "summary": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
                    + "また、旭川市の新型コロナワクチン接種医療機関の情報を、地図から探すことができる旭川市コロナワクチンマップも公開していますので、"
                    + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-02-27:/about",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/about",
                    "updated": "2022-02-27T00:00:00Z",
                    "title": "旭川市新型コロナウイルスまとめサイトについて",
                },
                {
                    "summary": "旭川市の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の予約受付状況などの情報を、地図から探すことができます。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_statuses",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市のコロナワクチンマップ（追加接種（オミクロン対応ワクチン））",
                },
                {
                    "summary": "旭川市の新型コロナワクチン接種医療機関（1・2回目接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/first_reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_statuses",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市のコロナワクチンマップ（1・2回目接種）",
                },
                {
                    "summary": "旭川市の新型コロナワクチン接種医療機関（5～11歳接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/child_reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_statuses",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市のコロナワクチンマップ（5～11歳接種）",
                },
                {
                    "summary": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/opendata",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/opendata",
                    "updated": "2022-01-29T07:00:00Z",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "summary": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果",
                },
                {
                    "summary": "西地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "西地区の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果",
                },
                {
                    "summary": "各条１７～２６丁目・宮前・南地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E5%90%84%E6%9D%A1%EF%BC%91%EF%BC%97%EF%BD%9E%EF%BC%92%EF%BC%96%"
                    + "E4%B8%81%E7%9B%AE%E3%83%BB%E5%AE%AE%E5%89%8D%E3%83%BB%E5%8D%97%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E5%90%84%E6%9D%A1%EF%BC%91%EF%BC%97%EF%BD%9E%EF%BC%92%EF%BC%96%"
                    + "E4%B8%81%E7%9B%AE%E3%83%BB%E5%AE%AE%E5%89%8D%E3%83%BB%E5%8D%97%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "各条１７～２６丁目・宮前・南地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果",
                },
                {
                    "summary": "新富・東・金星町地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E6%96%B0%E5%AF%8C%E3%83%BB%E6%9D%B1%E3%83%BB%E9%87%91%E6%98%9F%E7%94%BA%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/first_reservation_status/area/"
                    + "%E6%96%B0%E5%AF%8C%E3%83%BB%E6%9D%B1%E3%83%BB%E9%87%91%E6%98%9F%E7%94%BA%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "新富・東・金星町地区の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果",
                },
                {
                    "summary": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果",
                },
                {
                    "summary": "西地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/child_reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "西地区の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果",
                },
                {
                    "summary": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））",
                },
                {
                    "summary": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））",
                },
                {
                    "summary": "市立旭川病院の新型コロナワクチン接種予約受付状況（1・2回目接種）です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "市立旭川病院の新型コロナワクチン接種予約受付状況（1・2回目接種）",
                },
                {
                    "summary": "森山病院の新型コロナワクチン接種予約受付状況（1・2回目接種）です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E6%A3%AE%E5%B1%B1%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "first_reservation_status/medical_institution/"
                    + "%E6%A3%AE%E5%B1%B1%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "森山病院の新型コロナワクチン接種予約受付状況（1・2回目接種）",
                },
                {
                    "summary": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（5～11歳接種）です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川赤十字病院の新型コロナワクチン接種予約受付状況（5～11歳接種）",
                },
                {
                    "summary": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（5～11歳接種）です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/"
                    + "child_reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況（5～11歳接種）",
                },
            ],
        }
        result = atom.get_feed()
        assert result == expect
