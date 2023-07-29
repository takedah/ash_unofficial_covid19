from datetime import date, datetime, timezone

import pytest

from ash_unofficial_covid19.models.outpatient import OutpatientFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.outpatient import OutpatientService
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.services.press_release_link import PressReleaseLinkService
from ash_unofficial_covid19.views.xml import AtomView, RssView


@pytest.fixture()
def conn():
    # 発熱外来のセットアップ
    test_data = [
        {
            "is_outpatient": True,
            "is_positive_patients": True,
            "public_health_care_center": "旭川",
            "medical_institution_name": "市立旭川病院",
            "city": "旭川市",
            "address": "旭川市金星町1丁目1番65号",
            "phone_number": "0166-24-3181",
            "is_target_not_family": False,
            "is_pediatrics": True,
            "mon": "08:30～17:00",
            "tue": "08:30～17:00",
            "wed": "08:30～17:00",
            "thu": "08:30～17:00",
            "fri": "08:30～17:00",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": True,
            "is_online_for_positive_patients": True,
            "is_home_visitation_for_positive_patients": False,
            "memo": "かかりつけ患者及び保健所からの紹介患者に限ります。 https://www.city.asahikawa.hokkaido.jp/hospital/3100/d075882.html",
        },
        {
            "is_outpatient": True,
            "is_positive_patients": False,
            "public_health_care_center": "旭川",
            "medical_institution_name": "JA北海道厚生連旭川厚生病院",
            "city": "旭川市",
            "address": "旭川市1条通24丁目111番地",
            "phone_number": "0166-33-7171",
            "is_target_not_family": True,
            "is_pediatrics": False,
            "mon": "08:30～11:30",
            "tue": "08:30～11:30",
            "wed": "08:30～11:30",
            "thu": "08:30～11:30",
            "fri": "08:30～11:30",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": False,
            "is_online_for_positive_patients": False,
            "is_home_visitation_for_positive_patients": False,
            "memo": "",
        },
        {
            "is_outpatient": True,
            "is_positive_patients": True,
            "public_health_care_center": "旭川",
            "medical_institution_name": "旭川赤十字病院",
            "city": "旭川市",
            "address": "旭川市曙1条1丁目1番1号",
            "phone_number": "0166-22-8111",
            "is_target_not_family": False,
            "is_pediatrics": False,
            "mon": "",
            "tue": "",
            "wed": "",
            "thu": "",
            "fri": "",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": True,
            "is_online_for_positive_patients": False,
            "is_home_visitation_for_positive_patients": False,
            "memo": "「受診・相談センター」または保健所等の指示によら ず 受診した場合,初診時選定療養費を申し受けます。 当番制のため、不定期となっています。詳細はお問い合わせください。",
        },
        {
            "is_outpatient": False,
            "is_positive_patients": True,
            "public_health_care_center": "旭川",
            "medical_institution_name": "おうみや内科クリニック",
            "city": "旭川市",
            "address": "旭川市東光14条5丁目6番6号",
            "phone_number": "0166-39-3636",
            "is_target_not_family": True,
            "is_pediatrics": False,
            "mon": "",
            "tue": "",
            "wed": "",
            "thu": "",
            "fri": "",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": False,
            "is_online_for_positive_patients": False,
            "is_home_visitation_for_positive_patients": False,
            "memo": "",
        },
    ]
    factory = OutpatientFactory()
    for row in test_data:
        factory.create(**row)

    conn = ConnectionPool()
    service = OutpatientService(conn)
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
            OutpatientService, "get_last_updated", return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc)
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
                    "description": "旭川市の新型コロナ発熱外来の情報を、地図から探すことができます。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/outpatients",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatients",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市の新型コロナ発熱外来検索",
                },
                {
                    "description": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "guid": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/opendata",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/opendata",
                    "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "description": "JA北海道厚生連旭川厚生病院の新型コロナ発熱外来の情報です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "JA%E5%8C%97%E6%B5%B7%E9%81%93%E5%8E%9A%E7%94%9F%E9%80%A3%E6%97%AD%E5%B7%9D%E5%8E%9A%E7%94%9F%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "JA%E5%8C%97%E6%B5%B7%E9%81%93%E5%8E%9A%E7%94%9F%E9%80%A3%E6%97%AD%E5%B7%9D%E5%8E%9A%E7%94%9F%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "JA北海道厚生連旭川厚生病院の新型コロナ発熱外来の情報",
                },
                {
                    "description": "おうみや内科クリニックの新型コロナ発熱外来の情報です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E3%81%8A%E3%81%86%E3%81%BF%E3%82%84%E5%86%85%E7%A7%91%E3%82%AF%E3%83%AA%E3%83%8B%E3%83%83%E3%82%AF",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E3%81%8A%E3%81%86%E3%81%BF%E3%82%84%E5%86%85%E7%A7%91%E3%82%AF%E3%83%AA%E3%83%8B%E3%83%83%E3%82%AF",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "おうみや内科クリニックの新型コロナ発熱外来の情報",
                },
                {
                    "description": "市立旭川病院の新型コロナ発熱外来の情報です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "市立旭川病院の新型コロナ発熱外来の情報",
                },
                {
                    "description": "旭川赤十字病院の新型コロナ発熱外来の情報です。",
                    "guid": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川赤十字病院の新型コロナ発熱外来の情報",
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
            OutpatientService, "get_last_updated", return_value=datetime(2022, 3, 20, 0, 0, tzinfo=timezone.utc)
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
                    "summary": "旭川市の新型コロナ発熱外来の情報を、地図から探すことができます。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-03-20:/outpatients",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatients",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市の新型コロナ発熱外来検索",
                },
                {
                    "summary": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "id": "tag:covid19.asahikawa-opendata.morori.jp,2022-01-29:/opendata",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/opendata",
                    "updated": "2022-01-29T07:00:00Z",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "summary": "JA北海道厚生連旭川厚生病院の新型コロナ発熱外来の情報です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "JA%E5%8C%97%E6%B5%B7%E9%81%93%E5%8E%9A%E7%94%9F%E9%80%A3%E6%97%AD%E5%B7%9D%E5%8E%9A%E7%94%9F%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "JA%E5%8C%97%E6%B5%B7%E9%81%93%E5%8E%9A%E7%94%9F%E9%80%A3%E6%97%AD%E5%B7%9D%E5%8E%9A%E7%94%9F%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "JA北海道厚生連旭川厚生病院の新型コロナ発熱外来の情報",
                },
                {
                    "summary": "おうみや内科クリニックの新型コロナ発熱外来の情報です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E3%81%8A%E3%81%86%E3%81%BF%E3%82%84%E5%86%85%E7%A7%91%E3%82%AF%E3%83%AA%E3%83%8B%E3%83%83%E3%82%AF",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E3%81%8A%E3%81%86%E3%81%BF%E3%82%84%E5%86%85%E7%A7%91%E3%82%AF%E3%83%AA%E3%83%8B%E3%83%83%E3%82%AF",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "おうみや内科クリニックの新型コロナ発熱外来の情報",
                },
                {
                    "summary": "市立旭川病院の新型コロナ発熱外来の情報です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "市立旭川病院の新型コロナ発熱外来の情報",
                },
                {
                    "summary": "旭川赤十字病院の新型コロナ発熱外来の情報です。",
                    "id": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "link": "https://covid19.asahikawa-opendata.morori.jp/outpatient/medical_institution/"
                    + "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川赤十字病院の新型コロナ発熱外来の情報",
                },
            ],
        }
        result = atom.get_feed()
        assert result == expect
