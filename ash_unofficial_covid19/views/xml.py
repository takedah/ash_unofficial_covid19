from datetime import date, datetime, time, timezone

from ..config import Config
from ..services.database import ConnectionPool
from ..views.patients_number import DailyTotalView, PerHundredThousandPopulationView
from ..views.reservation_status import ReservationStatusView
from ..views.view import View


class XmlView(View):
    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): グラフを作成する基準日
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        self.__today = today
        self.__pool = pool
        last_modified = self._get_last_modified()
        self.__last_modified = last_modified
        self.__my_domain = Config.MY_DOMAIN
        self.__title = "旭川市新型コロナウイルスまとめサイト"
        self.__link = "https://" + Config.MY_DOMAIN + "/"
        self.__description = (
            "旭川市が公式ホームページで公表している新型コロナウイルスの情報を、機械判読しやすい形に変換したものを公開しています。"
            + "また、旭川市の新型コロナワクチン接種医療機関、新型コロナ発熱外来の情報を、地図から探すことができる検索アプリも公開していますので、"
            + "旭川の方はもとより、お引越しで新たに旭川に来られた方にぜひ使っていただきたいです。"
        )
        self.__index_feed = self._get_index_feed()
        self.__about_feed = self._get_about_feed()
        self.__reservation_status_feed = self._get_reservation_status_feed()
        self.__opendata_feed = self._get_opendata_feed()

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

    def _get_last_modified(self) -> datetime:
        """最新の報道発表日を返す

        時刻は旭川市公式ホームページの発表に合わせて16時固定とする。

        Returns:
            last_modified (datetime): 最終更新日の文字列

        """
        last_modified_date = self.__today
        # 時刻は16時固定とするが、UTCとしたいので7時とする
        last_modified_time = time(7, 0, 0, tzinfo=timezone.utc)
        last_modified = datetime.combine(last_modified_date, last_modified_time)

        return last_modified.astimezone(timezone.utc)

    def _get_index_feed(self) -> dict:
        """トップページのFeed用データを返す

        Returns:
            feed_data (dict): トップページのFeed用データ

        """
        title = self.__today.strftime("%Y/%m/%d (%a)") + " の旭川市新型コロナウイルス感染者数の推移"
        link = "https://" + self.my_domain + "/"
        daily_total = DailyTotalView(self.__today, self.__pool)
        most_recent = daily_total.most_recent
        increase_from_seven_days_before = daily_total.increase_from_seven_days_before
        per_hundred_thousand_population = PerHundredThousandPopulationView(self.__today, self.__pool)
        this_week = per_hundred_thousand_population.this_week
        increase_from_last_week = per_hundred_thousand_population.increase_from_last_week
        description = (
            self.__today.strftime("%Y/%m/%d (%a)")
            + " の旭川市の新型コロナ新規感染者数は"
            + most_recent
            + "人で、先週の同じ曜日から"
            + increase_from_seven_days_before
            + "人でした。"
            + "直近1週間の人口10万人あたりの新規感染者数は"
            + this_week
            + "人で、先週から"
            + increase_from_last_week
            + "人となっています。"
        )
        pub_date = self.last_modified
        guid = "tag:" + self.my_domain + "," + self.__today.strftime("%Y-%m-%d") + ":/"
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
        """新型コロナワクチン接種医療機関検索アプリのFeed用データを返す

        Returns:
            feed_data (dict): 新型コロナワクチン接種医療機関検索アプリのFeed用データ

        """
        title = "旭川市の新型コロナワクチン接種医療機関検索アプリ"
        link = "https://" + self.my_domain + "/reservation_statuses"
        description = "旭川市の新型コロナワクチン接種医療機関の予約受付状況などの情報を、地図から探すことができます。"
        view = ReservationStatusView(self.__pool)
        pub_date = view.get_last_updated()
        pub_date = pub_date.astimezone(timezone.utc)
        guid = "tag:" + self.my_domain + "," + pub_date.strftime("%Y-%m-%d") + ":/reservation_statuses"
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
        """新型コロナワクチン接種医療機関検索アプリの地区一覧Feed用データを返す

        Returns:
            feed_data_list (list): 新型コロナワクチン接種医療機関検索アプリの地区一覧Feed用データのリスト

        """
        view = ReservationStatusView(self.__pool)
        area_list = view.get_area_list()
        feed_data_list = list()
        for area in area_list:
            title = area["name"] + "の新型コロナワクチン接種医療機関の検索結果"
            link = "https://" + self.my_domain + "/reservation_status/area/" + area["url"]
            description = title + "です。"
            pub_date = view.get_last_updated()
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
        """新型コロナワクチン接種医療機関検索アプリの医療機関一覧Feed用データを返す

        Returns:
            feed_data_list (list): 新型コロナワクチン接種医療機関検索アプリの医療機関一覧Feed用データのリスト

        """
        view = ReservationStatusView(self.__pool)
        medical_institution_list = view.get_medical_institution_list()
        feed_data_list = list()
        for medical_institution in medical_institution_list:
            title = medical_institution["name"] + "の新型コロナワクチン接種予約受付状況"
            link = (
                "https://" + self.my_domain + "/reservation_status/medical_institution/" + medical_institution["url"]
            )
            description = title + "です。"
            pub_date = view.get_last_updated()
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
    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): 基準日

        """
        XmlView.__init__(self, today, pool)

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
            self._get_item(self.opendata_feed),
        ]

        # 地区一覧を追加
        area_feed_list = self.get_reservation_status_area_feed_list()
        for area_feed in area_feed_list:
            items.append(self._get_item(area_feed))

        # 医療機関一覧を追加
        medical_institution_feed_list = self.get_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in medical_institution_feed_list:
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
    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): 基準日

        """
        XmlView.__init__(self, today, pool)

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
            self._get_item(self.opendata_feed),
        ]

        # 地区一覧を追加
        area_feed_list = self.get_reservation_status_area_feed_list()
        for area_feed in area_feed_list:
            entries.append(self._get_item(area_feed))

        # 医療機関一覧を追加
        medical_institution_feed_list = self.get_reservation_status_medical_institution_feed_list()
        for medical_institution_feed in medical_institution_feed_list:
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
