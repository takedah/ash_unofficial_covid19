from datetime import date, datetime, time, timezone
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta

from ..config import Config
from ..services.child_reservation_status import ChildReservationStatusService
from ..services.first_reservation_status import FirstReservationStatusService
from ..services.patients_number import PatientsNumberService
from ..services.press_release_link import PressReleaseLinkService
from ..services.reservation_status import ReservationStatusService
from ..views.child_reservation_status import ChildReservationStatusView
from ..views.first_reservation_status import FirstReservationStatusView
from ..views.reservation_status import ReservationStatusView


class XmlView:
    def __init__(self):
        today = self._get_today()
        self.__today = today
        last_modified = self._get_last_modified()
        self.__last_modified = last_modified
        self.__my_domain = Config.MY_DOMAIN
        self.__title = "旭川市新型コロナウイルスまとめサイト"
        self.__link = "https://" + Config.MY_DOMAIN + "/"
        self.__description = (
            "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
            + "また、旭川市の新型コロナワクチン接種医療機関の情報を、地図から探すことができる旭川市コロナワクチンマップも公開していますので、"
            + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。"
        )
        self.__index_feed = self._get_index_feed()
        self.__about_feed = self._get_about_feed()
        self.__reservation_status_feed = self._get_reservation_status_feed()
        self.__first_reservation_status_feed = self._get_first_reservation_status_feed()
        self.__child_reservation_status_feed = self._get_child_reservation_status_feed()
        self.__opendata_feed = self._get_opendata_feed()

    @property
    def today(self):
        return self.__today

    @property
    def last_modified(self):
        return self.__last_modified

    @property
    def my_domain(self):
        return self.__my_domain

    @property
    def title(self):
        return self.__title

    @property
    def link(self):
        return self.__link

    @property
    def description(self):
        return self.__description

    @property
    def index_feed(self):
        return self.__index_feed

    @property
    def about_feed(self):
        return self.__about_feed

    @property
    def reservation_status_feed(self):
        return self.__reservation_status_feed

    @property
    def first_reservation_status_feed(self):
        return self.__first_reservation_status_feed

    @property
    def child_reservation_status_feed(self):
        return self.__child_reservation_status_feed

    @property
    def opendata_feed(self):
        return self.__opendata_feed

    def get_last_modified_header(self) -> str:
        """HTTP Last Modifiedヘッダー用文字列を出力

        ATOM FeedとRSS Feed用に最終更新日をHTTP Headerに出力させるため、
        最新の報道発表日を文字列で出力する。時刻は旭川市公式ホームページの発表に合わせて16時固定とする。

        Returns:
            last_modified_header (str): 最終更新日の文字列

        """
        last_modified = self._get_last_modified()
        return last_modified.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    def _get_today(self) -> date:
        """グラフの基準となる最新の報道発表日の日付を返す

        Returns:
            today (date): 最新の報道発表日の日付データ

        """
        press_release_link_service = PressReleaseLinkService()
        return press_release_link_service.get_latest_publication_date()

    def _get_last_modified(self) -> datetime:
        """最新の報道発表日を返す

        時刻は旭川市公式ホームページの発表に合わせて16時固定とする。

        Returns:
            last_modified (datetime): 最終更新日の文字列

        """
        last_modified_date = self._get_today()
        # 時刻は16時固定とするが、UTCとしたいので7時とする
        last_modified_time = time(7, 0, 0, tzinfo=timezone.utc)
        last_modified = datetime.combine(last_modified_date, last_modified_time)

        return last_modified.astimezone(timezone.utc)

    def _get_index_feed(self) -> dict:
        """トップページのFeed用データを返す

        Returns:
            feed_data (dict): トップページのFeed用データ

        """
        title = self.today.strftime("%Y/%m/%d (%a)") + " の旭川市内感染状況の最新動向"
        link = "https://" + self.my_domain + "/"
        last_week = self.today - relativedelta(days=7)
        patients_number_service = PatientsNumberService()
        daily_total_data = patients_number_service.get_aggregate_by_days(from_date=last_week, to_date=self.today)
        most_recent = daily_total_data[-1][1]
        seven_days_before_most_recent = daily_total_data[-8][1]
        increase_from_seven_days_before = most_recent - seven_days_before_most_recent
        week_before_last = self.today - relativedelta(weeks=2, days=-1)
        per_hundred_thousand_population_data = patients_number_service.get_per_hundred_thousand_population_per_week(
            from_date=week_before_last, to_date=self.today
        )
        this_week_per = per_hundred_thousand_population_data[-1][1]
        last_week_per = per_hundred_thousand_population_data[-2][1]
        increase_from_last_week_per = float(
            Decimal(str(this_week_per - last_week_per)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        description = (
            self.today.strftime("%Y/%m/%d (%a)")
            + " の旭川市の新型コロナ新規感染者数は"
            + "{:,}".format(most_recent)
            + "人で、先週の同じ曜日から"
            + "{:+,}".format(increase_from_seven_days_before)
            + "人でした。"
            + "直近1週間の人口10万人あたりの新規感染者数は"
            + "{:,}".format(this_week_per)
            + "人で、先週から"
            + "{:+,}".format(increase_from_last_week_per)
            + "人となっています。"
        )
        pub_date = self.last_modified
        guid = "tag:" + self.my_domain + "," + self.today.strftime("%Y-%m-%d") + ":/"
        return {
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "guid": guid,
        }

    def _get_about_feed(self) -> dict:
        """このサイトについてのFeed用データを返す

        Returns:
            feed_data (dict): このサイトについてのFeed用データ

        """
        title = "旭川市新型コロナウイルスまとめサイトについて"
        link = "https://" + self.my_domain + "/about"
        description = self.description
        pub_date = datetime(2022, 2, 27, 0, 0, tzinfo=timezone.utc)
        guid = "tag:" + self.my_domain + "," + pub_date.strftime("%Y-%m-%d") + ":/about"
        return {
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "guid": guid,
        }

    def _get_reservation_status_feed(self) -> dict:
        """コロナワクチンマップ（追加接種（オミクロン対応ワクチン））のFeed用データを返す

        Returns:
            feed_data (dict): コロナワクチンマップ（追加接種（オミクロン対応ワクチン））のFeed用データ

        """
        title = "旭川市のコロナワクチンマップ（追加接種（オミクロン対応ワクチン））"
        link = "https://" + self.my_domain + "/reservation_statuses"
        description = "旭川市の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の予約受付状況などの情報を、地図から探すことができます。"
        service = ReservationStatusService()
        pub_date = service.get_last_updated()
        pub_date = pub_date.astimezone(timezone.utc)
        guid = "tag:" + self.my_domain + "," + pub_date.strftime("%Y-%m-%d") + ":/reservation_statuses"
        return {
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "guid": guid,
        }

    def _get_first_reservation_status_feed(self) -> dict:
        """コロナワクチンマップ（1・2回目接種）のFeed用データを返す

        Returns:
            feed_data (dict): コロナワクチンマップ（1・2回目接種）のFeed用データ

        """
        title = "旭川市のコロナワクチンマップ（1・2回目接種）"
        link = "https://" + self.my_domain + "/first_reservation_statuses"
        description = "旭川市の新型コロナワクチン接種医療機関（1・2回目接種）の予約受付状況などの情報を、地図から探すことができます。"
        service = FirstReservationStatusService()
        pub_date = service.get_last_updated()
        pub_date = pub_date.astimezone(timezone.utc)
        guid = "tag:" + self.my_domain + "," + pub_date.strftime("%Y-%m-%d") + ":/first_reservation_statuses"
        return {
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "guid": guid,
        }

    def _get_child_reservation_status_feed(self) -> dict:
        """コロナワクチンマップ（5～11歳接種）のFeed用データを返す

        Returns:
            feed_data (dict): コロナワクチンマップ（5～11歳接種）のFeed用データ

        """
        title = "旭川市のコロナワクチンマップ（5～11歳接種）"
        link = "https://" + self.my_domain + "/first_reservation_statuses"
        description = "旭川市の新型コロナワクチン接種医療機関（5～11歳接種）の予約受付状況などの情報を、地図から探すことができます。"
        service = ChildReservationStatusService()
        pub_date = service.get_last_updated()
        pub_date = pub_date.astimezone(timezone.utc)
        guid = "tag:" + self.my_domain + "," + pub_date.strftime("%Y-%m-%d") + ":/child_reservation_statuses"
        return {
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "guid": guid,
        }

    def _get_opendata_feed(self) -> dict:
        """非公式オープンデータのFeed用データを返す

        Returns:
            feed_data (dict): 非公式オープンデータのFeed用データ

        """
        guid = "https://" + self.my_domain + "/opendata"
        title = "旭川市新型コロナウイルス感染症非公式オープンデータ"
        link = guid
        description = "旭川市が公式ホームページで公表している新型コロナウイルスに関する情報を、CSVやJSONといった機械判読しやすい形に変換したものを公開しています。"
        pub_date = self.last_modified
        guid = "tag:" + self.my_domain + "," + pub_date.strftime("%Y-%m-%d") + ":/opendata"
        return {
            "title": title,
            "link": link,
            "description": description,
            "pub_date": pub_date,
            "guid": guid,
        }

    def get_feed(self):
        pass

    def get_reservation_status_area_feed_list(self) -> list:
        """コロナワクチンマップ（追加接種（オミクロン対応ワクチン））の地区一覧Feed用データを返す

        Returns:
            feed_data_list (list): コロナワクチンマップ（追加接種（オミクロン対応ワクチン））の地区一覧Feed用データのリスト

        """
        service = ReservationStatusService()
        view = ReservationStatusView()
        area_list = view.get_area_list()
        feed_data_list = list()
        for area in area_list:
            title = area["name"] + "の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果"
            link = "https://" + self.my_domain + "/reservation_status/area/" + area["url"]
            description = title + "です。"
            pub_date = service.get_last_updated()
            pub_date = pub_date.astimezone(timezone.utc)
            guid = link
            feed_data_list.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date,
                    "guid": guid,
                }
            )

        return feed_data_list

    def get_reservation_status_medical_institution_feed_list(self) -> list:
        """コロナワクチンマップ（追加接種（オミクロン対応ワクチン））の医療機関一覧Feed用データを返す

        Returns:
            feed_data_list (list): コロナワクチンマップ（追加接種（オミクロン対応ワクチン））の医療機関一覧Feed用データのリスト

        """
        service = ReservationStatusService()
        view = ReservationStatusView()
        medical_institution_list = view.get_medical_institution_list()
        feed_data_list = list()
        for medical_institution in medical_institution_list:
            title = medical_institution["name"] + "の新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））"
            link = (
                "https://" + self.my_domain + "/reservation_status/medical_institution/" + medical_institution["url"]
            )
            description = title + "です。"
            pub_date = service.get_last_updated()
            pub_date = pub_date.astimezone(timezone.utc)
            guid = link
            feed_data_list.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date,
                    "guid": guid,
                }
            )

        return feed_data_list

    def get_first_reservation_status_area_feed_list(self) -> list:
        """コロナワクチンマップ（1・2回目接種）の地区一覧Feed用データを返す

        Returns:
            feed_data_list (list): コロナワクチンマップ（1・2回目接種）の地区一覧Feed用データのリスト

        """
        service = FirstReservationStatusService()
        view = FirstReservationStatusView()
        area_list = view.get_area_list()
        feed_data_list = list()
        for area in area_list:
            title = area["name"] + "の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果"
            link = "https://" + self.my_domain + "/first_reservation_status/area/" + area["url"]
            description = title + "です。"
            pub_date = service.get_last_updated()
            pub_date = pub_date.astimezone(timezone.utc)
            guid = link
            feed_data_list.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date,
                    "guid": guid,
                }
            )

        return feed_data_list

    def get_first_reservation_status_medical_institution_feed_list(self) -> list:
        """コロナワクチンマップ（1・2回目接種）の医療機関一覧Feed用データを返す

        Returns:
            feed_data_list (list): コロナワクチンマップ（1・2回目接種）の医療機関一覧Feed用データのリスト

        """
        service = FirstReservationStatusService()
        view = FirstReservationStatusView()
        medical_institution_list = view.get_medical_institution_list()
        feed_data_list = list()
        for medical_institution in medical_institution_list:
            title = medical_institution["name"] + "の新型コロナワクチン接種予約受付状況（1・2回目接種）"
            link = (
                "https://"
                + self.my_domain
                + "/first_reservation_status/medical_institution/"
                + medical_institution["url"]
            )
            description = title + "です。"
            pub_date = service.get_last_updated()
            pub_date = pub_date.astimezone(timezone.utc)
            guid = link
            feed_data_list.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date,
                    "guid": guid,
                }
            )

        return feed_data_list

    def get_child_reservation_status_area_feed_list(self) -> list:
        """コロナワクチンマップ（5～11歳接種）の地区一覧Feed用データを返す

        Returns:
            feed_data_list (list): コロナワクチンマップ（5～11歳接種）の地区一覧Feed用データのリスト

        """
        service = ChildReservationStatusService()
        view = ChildReservationStatusView()
        area_list = view.get_area_list()
        feed_data_list = list()
        for area in area_list:
            title = area["name"] + "の新型コロナワクチン接種医療機関（5～11歳接種）の検索結果"
            link = "https://" + self.my_domain + "/child_reservation_status/area/" + area["url"]
            description = title + "です。"
            pub_date = service.get_last_updated()
            pub_date = pub_date.astimezone(timezone.utc)
            guid = link
            feed_data_list.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date,
                    "guid": guid,
                }
            )

        return feed_data_list

    def get_child_reservation_status_medical_institution_feed_list(self) -> list:
        """コロナワクチンマップ（5～11歳接種）の医療機関一覧Feed用データを返す

        Returns:
            feed_data_list (list): コロナワクチンマップ（5～11歳接種）の医療機関一覧Feed用データのリスト

        """
        service = ChildReservationStatusService()
        view = ChildReservationStatusView()
        medical_institution_list = view.get_medical_institution_list()
        feed_data_list = list()
        for medical_institution in medical_institution_list:
            title = medical_institution["name"] + "の新型コロナワクチン接種予約受付状況（5～11歳接種）"
            link = (
                "https://"
                + self.my_domain
                + "/child_reservation_status/medical_institution/"
                + medical_institution["url"]
            )
            description = title + "です。"
            pub_date = service.get_last_updated()
            pub_date = pub_date.astimezone(timezone.utc)
            guid = link
            feed_data_list.append(
                {
                    "title": title,
                    "link": link,
                    "description": description,
                    "pub_date": pub_date,
                    "guid": guid,
                }
            )

        return feed_data_list


class RssView(XmlView):
    def __init__(self):
        XmlView.__init__(self)

    def get_feed(self) -> dict:
        """RSS Feed文字列を返す

        Returns:
            feed (dict): RSS Feedのデータ

        """
        rss_url = "https://" + self.my_domain + "/rss.xml"
        last_modified = self.last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
        items = [
            self._get_item(self.index_feed),
            self._get_item(self.about_feed),
            self._get_item(self.reservation_status_feed),
            self._get_item(self.first_reservation_status_feed),
            self._get_item(self.child_reservation_status_feed),
            self._get_item(self.opendata_feed),
        ]

        # 地区一覧を追加
        area_feed_list = self.get_reservation_status_area_feed_list()
        for area_feed in area_feed_list:
            items.append(self._get_item(area_feed))

        first_area_feed_list = self.get_first_reservation_status_area_feed_list()
        for area_feed in first_area_feed_list:
            items.append(self._get_item(area_feed))

        child_area_feed_list = self.get_child_reservation_status_area_feed_list()
        for area_feed in child_area_feed_list:
            items.append(self._get_item(area_feed))

        # 医療機関一覧を追加
        medical_institution_feed_list = self.get_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in medical_institution_feed_list:
            items.append(self._get_item(medical_institution_feed))

        first_medical_institution_feed_list = self.get_first_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in first_medical_institution_feed_list:
            items.append(self._get_item(medical_institution_feed))

        child_medical_institution_feed_list = self.get_child_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in child_medical_institution_feed_list:
            items.append(self._get_item(medical_institution_feed))

        return {
            "title": self.title,
            "link": self.link,
            "description": self.description,
            "pub_date": last_modified,
            "last_build_date": last_modified,
            "rss_url": rss_url,
            "items": items,
        }

    @staticmethod
    def _get_item(xml_item: dict) -> dict:
        """RSSのItem要素用に辞書データを変換する

        Args:
            xml_item (dict): 変換前の辞書データ

        Returns:
            rss_item (dict): 変換後の辞書データ

        """
        return {
            "title": xml_item["title"],
            "link": xml_item["link"],
            "description": xml_item["description"],
            "pub_date": xml_item["pub_date"].strftime("%a, %d %b %Y %H:%M:%S GMT"),
            "guid": xml_item["guid"],
        }


class AtomView(XmlView):
    def __init__(self):
        XmlView.__init__(self)

    def get_feed(self) -> dict:
        """ATOM Feedデータ返す

        Returns:
            feed (dict): Atom Feedデータ

        """
        atom_url = "https://" + self.my_domain + "/atom.xml"
        last_modified = self.last_modified.strftime("%Y-%m-%dT%H:%M:%SZ")
        entries = [
            self._get_item(self.index_feed),
            self._get_item(self.about_feed),
            self._get_item(self.reservation_status_feed),
            self._get_item(self.first_reservation_status_feed),
            self._get_item(self.child_reservation_status_feed),
            self._get_item(self.opendata_feed),
        ]

        # 地区一覧を追加
        area_feed_list = self.get_reservation_status_area_feed_list()
        for area_feed in area_feed_list:
            entries.append(self._get_item(area_feed))

        first_area_feed_list = self.get_first_reservation_status_area_feed_list()
        for area_feed in first_area_feed_list:
            entries.append(self._get_item(area_feed))

        child_area_feed_list = self.get_child_reservation_status_area_feed_list()
        for area_feed in child_area_feed_list:
            entries.append(self._get_item(area_feed))

        # 医療機関一覧を追加
        medical_institution_feed_list = self.get_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in medical_institution_feed_list:
            entries.append(self._get_item(medical_institution_feed))

        first_medical_institution_feed_list = self.get_first_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in first_medical_institution_feed_list:
            entries.append(self._get_item(medical_institution_feed))

        child_medical_institution_feed_list = self.get_child_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in child_medical_institution_feed_list:
            entries.append(self._get_item(medical_institution_feed))

        return {
            "id": self.link,
            "title": self.title,
            "atom_url": atom_url,
            "updated": last_modified,
            "author": {
                "name": "takedah",
                "url": "https://github.com/takedah/ash_unofficial_covid19",
            },
            "entries": entries,
        }

    @staticmethod
    def _get_item(xml_item: dict) -> dict:
        """ATOMのEntry要素用に辞書データを変換する

        Args:
            xml_item (dict): 変換前の辞書データ

        Returns:
            atom_item (dict): 変換後の辞書データ

        """
        return {
            "title": xml_item["title"],
            "link": xml_item["link"],
            "summary": xml_item["description"],
            "updated": xml_item["pub_date"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            "id": xml_item["guid"],
        }
