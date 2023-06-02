from datetime import date, datetime, timezone

import pytest

from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.services.press_release_link import PressReleaseLinkService
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService
from ash_unofficial_covid19.views.xml import AtomView, RssView


@pytest.fixture()
def conn():
    test_data = [
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "division": "春開始接種（12歳以上）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "memo": "当院ホームページをご確認ください",
        },
        {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "division": "小児接種（３回目以降）",
            "vaccine": "ファイザー モデルナ",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": None,
            "memo": "",
        },
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "division": "小児接種（３回目以降）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "memo": "かかりつけ患者以外は※条件あり 当院ホームページをご確認ください",
        },
    ]
    factory = ReservationStatusFactory()
    for row in test_data:
        factory.create(**row)

    conn = ConnectionPool()
    service = ReservationStatusService(conn)
    service.create(factory)

    yield conn

    conn.close_connection()


class TestRssView:
    def test_get_feed(self, conn, mocker):
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
        rss = RssView(date(2022, 1, 29), conn)
        expect = {
            "title": "旭川市新型コロナウイルスまとめサイト",
            "link": "https://covid19.asahikawa-opendata.morori.jp/",
            "description": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
            + "また、旭川市の新型コロナワクチン接種医療機関、新型コロナ発熱外来の情報を、地図から探すことができる検索アプリも公開していますので、"
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
                    "title": "2022/01/29 (Sat) の旭川市新型コロナウイルス感染者数の推移",
                },
                {
                    "description": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
                    + "また、旭川市の新型コロナワクチン接種医療機関、新型コロナ発熱外来の情報を、地図から探すことができる検索アプリも公開していますので、"
                    + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-02-27:/about",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/about",
                    "pub_date": "Sun, 27 Feb 2022 00:00:00 GMT",
                    "title": "旭川市新型コロナウイルスまとめサイトについて",
                },
                {
                    "description": "旭川市の新型コロナワクチン接種医療機関の予約受付状況などの情報を、地図から探すことができます。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_statuses",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市の新型コロナワクチン接種医療機関検索アプリ",
                },
                {
                    "description": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/opendata",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/opendata",
                    "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "description": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関の検索結果",
                },
                {
                    "description": "西地区の新型コロナワクチン接種医療機関の検索結果です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "西地区の新型コロナワクチン接種医療機関の検索結果",
                },
                {
                    "description": "旭川赤十字病院の新型コロナワクチン接種予約受付状況です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川赤十字病院の新型コロナワクチン接種予約受付状況",
                },
                {
                    "description": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況",
                },
            ],
        }
        result = rss.get_feed()
        assert result == expect


class TestAtomView:
    def test_get_feed(self, conn, mocker):
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
        atom = AtomView(date(2022, 1, 29), conn)
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
                    "title": "2022/01/29 (Sat) の旭川市新型コロナウイルス感染者数の推移",
                },
                {
                    "summary": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
                    + "また、旭川市の新型コロナワクチン接種医療機関、新型コロナ発熱外来の情報を、地図から探すことができる検索アプリも公開していますので、"
                    + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-02-27:/about",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/about",
                    "updated": "2022-02-27T00:00:00Z",
                    "title": "旭川市新型コロナウイルスまとめサイトについて",
                },
                {
                    "summary": "旭川市の新型コロナワクチン接種医療機関の予約受付状況などの情報を、地図から探すことができます。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/reservation_statuses",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_statuses",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市の新型コロナワクチン接種医療機関検索アプリ",
                },
                {
                    "summary": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/opendata",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/opendata",
                    "updated": "2022-01-29T07:00:00Z",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "summary": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%8A%B1%E5%92%B2%E7%94%BA%E3%83%BB%E6%9C%AB%E5%BA%83%E3%83%BB%"
                    + "E6%9C%AB%E5%BA%83%E6%9D%B1%E3%83%BB%E6%9D%B1%E9%B7%B9%E6%A0%96%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "花咲町・末広・末広東・東鷹栖地区の新型コロナワクチン接種医療機関の検索結果",
                },
                {
                    "summary": "西地区の新型コロナワクチン接種医療機関の検索結果です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/area/"
                    + "%E8%A5%BF%E5%9C%B0%E5%8C%BA",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "西地区の新型コロナワクチン接種医療機関の検索結果",
                },
                {
                    "summary": "旭川赤十字病院の新型コロナワクチン接種予約受付状況です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川赤十字病院の新型コロナワクチン接種予約受付状況",
                },
                {
                    "summary": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/reservation_status/medical_institution/"
                    + "%E7%8B%AC%E7%AB%8B%E8%A1%8C%E6%94%BF%E6%B3%95%E4%BA%BA%E5%9B%BD%"
                    + "E7%AB%8B%E7%97%85%E9%99%A2%E6%A9%9F%E6%A7%8B%E6%97%AD%E5%B7%9D%E"
                    + "5%8C%BB%E7%99%82%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "独立行政法人国立病院機構旭川医療センターの新型コロナワクチン接種予約受付状況",
                },
            ],
        }
        result = atom.get_feed()
        assert result == expect
