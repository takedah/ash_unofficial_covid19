from datetime import date, datetime, timezone

from ash_unofficial_covid19.services.child_reservation_status import ChildReservationStatusService
from ash_unofficial_covid19.services.first_reservation_status import FirstReservationStatusService
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.services.press_release_link import PressReleaseLinkService
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService
from ash_unofficial_covid19.views.xml import AtomView, RssView


class TestRssView:
    def test_get_feed(self, mocker):
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
        rss = RssView()
        expect = {
            "title": "旭川市新型コロナウイルスまとめサイト",
            "link": "https://ash-unofficial-covid19.herokuapp.com/",
            "description": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
            + "また、旭川市の新型コロナワクチン接種医療機関の情報を、地図から探すことができる旭川市コロナワクチンマップも公開していますので、"
            + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
            "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
            "last_build_date": "Sat, 29 Jan 2022 07:00:00 GMT",
            "rss_url": "https://ash-unofficial-covid19.herokuapp.com/rss.xml",
            "items": [
                {
                    "description": "2022/01/29 (Sat) の旭川市の新型コロナ新規感染者数は102人で、先週の同じ曜日から+102人でした。"
                    + "直近1週間の人口10万人あたりの新規感染者数は60.05人で、先週から+60.05人となっています。",
                    "guid": "tag:ash-unofficial-covid19.herokuapp.com,2022-01-29:/",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/",
                    "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
                    "title": "2022/01/29 (Sat) の旭川市内感染状況の最新動向",
                },
                {
                    "description": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
                    + "また、旭川市の新型コロナワクチン接種医療機関の情報を、地図から探すことができる旭川市コロナワクチンマップも公開していますので、"
                    + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
                    "guid": "tag:ash-unofficial-covid19.herokuapp.com,2022-02-27:/about",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/about",
                    "pub_date": "Sun, 27 Feb 2022 00:00:00 GMT",
                    "title": "旭川市新型コロナウイルスまとめサイトについて",
                },
                {
                    "description": "旭川市の新型コロナワクチン接種医療機関（3回目接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "guid": "tag:ash-unofficial-covid19.herokuapp.com,2022-03-20:/reservation_statuses",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/reservation_statuses",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市のコロナワクチンマップ（3回目接種）",
                },
                {
                    "description": "旭川市の新型コロナワクチン接種医療機関（1・2回目接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "guid": "tag:ash-unofficial-covid19.herokuapp.com,2022-03-20:/first_reservation_statuses",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/first_reservation_statuses",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市のコロナワクチンマップ（1・2回目接種）",
                },
                {
                    "description": "旭川市の新型コロナワクチン接種医療機関（5～11歳接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "guid": "tag:ash-unofficial-covid19.herokuapp.com,2022-03-20:/child_reservation_statuses",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/first_reservation_statuses",
                    "pub_date": "Sun, 20 Mar 2022 00:00:00 GMT",
                    "title": "旭川市のコロナワクチンマップ（5～11歳接種）",
                },
                {
                    "description": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "guid": "tag:ash-unofficial-covid19.herokuapp.com,2022-01-29:/opendata",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/opendata",
                    "pub_date": "Sat, 29 Jan 2022 07:00:00 GMT",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "description": "2022年1月27日発表分をもって旭川市が感染者ごとの情報の公表をやめたため、同日時点までの情報を表示しています。",
                    "guid": "tag:ash-unofficial-covid19.herokuapp.com,2022-01-27:/patients",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/patients",
                    "pub_date": "Thu, 27 Jan 2022 00:00:00 GMT",
                    "title": "旭川市の新型コロナウイルス感染症患者の状況",
                },
            ],
        }
        result = rss.get_feed()
        assert result == expect


class TestAtomView:
    def test_get_feed(self, mocker):
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
        rss = AtomView()
        expect = {
            "id": "https://ash-unofficial-covid19.herokuapp.com/",
            "title": "旭川市新型コロナウイルスまとめサイト",
            "atom_url": "https://ash-unofficial-covid19.herokuapp.com/atom.xml",
            "author": {
                "name": "takedah",
                "url": "https://github.com/takedah/ash_unofficial_covid19",
            },
            "updated": "2022-01-29T07:00:00Z",
            "entries": [
                {
                    "summary": "2022/01/29 (Sat) の旭川市の新型コロナ新規感染者数は102人で、先週の同じ曜日から+102人でした。"
                    + "直近1週間の人口10万人あたりの新規感染者数は60.05人で、先週から+60.05人となっています。",
                    "id": "tag:ash-unofficial-covid19.herokuapp.com,2022-01-29:/",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/",
                    "updated": "2022-01-29T07:00:00Z",
                    "title": "2022/01/29 (Sat) の旭川市内感染状況の最新動向",
                },
                {
                    "summary": "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
                    + "また、旭川市の新型コロナワクチン接種医療機関の情報を、地図から探すことができる旭川市コロナワクチンマップも公開していますので、"
                    + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。",
                    "id": "tag:ash-unofficial-covid19.herokuapp.com,2022-02-27:/about",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/about",
                    "updated": "2022-02-27T00:00:00Z",
                    "title": "旭川市新型コロナウイルスまとめサイトについて",
                },
                {
                    "summary": "旭川市の新型コロナワクチン接種医療機関（3回目接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "id": "tag:ash-unofficial-covid19.herokuapp.com,2022-03-20:/reservation_statuses",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/reservation_statuses",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市のコロナワクチンマップ（3回目接種）",
                },
                {
                    "summary": "旭川市の新型コロナワクチン接種医療機関（1・2回目接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "id": "tag:ash-unofficial-covid19.herokuapp.com,2022-03-20:/first_reservation_statuses",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/first_reservation_statuses",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市のコロナワクチンマップ（1・2回目接種）",
                },
                {
                    "summary": "旭川市の新型コロナワクチン接種医療機関（5～11歳接種）の予約受付状況などの情報を、地図から探すことができます。",
                    "id": "tag:ash-unofficial-covid19.herokuapp.com,2022-03-20:/child_reservation_statuses",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/first_reservation_statuses",
                    "updated": "2022-03-20T00:00:00Z",
                    "title": "旭川市のコロナワクチンマップ（5～11歳接種）",
                },
                {
                    "summary": "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。",
                    "id": "tag:ash-unofficial-covid19.herokuapp.com,2022-01-29:/opendata",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/opendata",
                    "updated": "2022-01-29T07:00:00Z",
                    "title": "旭川市新型コロナウイルス感染症非公式オープンデータ",
                },
                {
                    "summary": "2022年1月27日発表分をもって旭川市が感染者ごとの情報の公表をやめたため、同日時点までの情報を表示しています。",
                    "id": "tag:ash-unofficial-covid19.herokuapp.com,2022-01-27:/patients",
                    "link": "https://ash-unofficial-covid19.herokuapp.com/patients",
                    "updated": "2022-01-27T00:00:00Z",
                    "title": "旭川市の新型コロナウイルス感染症患者の状況",
                },
            ],
        }
        result = rss.get_feed()
        assert result == expect
