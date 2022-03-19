from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta

from ..config import Config
from ..errors import DatabaseConnectionError
from ..services.child_reservation_status import ChildReservationStatusService
from ..services.first_reservation_status import FirstReservationStatusService
from ..services.patients_number import PatientsNumberService
from ..services.press_release_link import PressReleaseLinkService
from ..services.reservation_status import ReservationStatusService


class XmlView:
    def __init__(self):
        today = self._get_today()
        last_week = today - relativedelta(days=7)
        daily_total_data = self._get_aggregate_by_days(from_date=last_week, to_date=today)
        most_recent = daily_total_data[-1][1]
        seven_days_before_most_recent = daily_total_data[-8][1]
        increase_from_seven_days_before = most_recent - seven_days_before_most_recent
        week_before_last = today - relativedelta(weeks=2, days=-1)
        per_hundred_thousand_population_data = self._get_per_hundred_thousand_population_per_week(
            from_date=week_before_last, to_date=today
        )
        this_week_per = per_hundred_thousand_population_data[-1][1]
        last_week_per = per_hundred_thousand_population_data[-2][1]
        increase_from_last_week_per = float(
            Decimal(str(this_week_per - last_week_per)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        self.__this_week_per = "{:,}".format(this_week_per)
        self.__increase_from_last_week_per = "{:+,}".format(increase_from_last_week_per)
        self.__today = today
        self.__most_recent = "{:,}".format(most_recent)
        self.__increase_from_seven_days_before = "{:+,}".format(increase_from_seven_days_before)
        self.__reservation_status_updated = self._get_reservation_status_updated()
        self.__first_reservation_status_updated = self._get_first_reservation_status_updated()
        self.__child_reservation_status_updated = self._get_child_reservation_status_updated()

    @property
    def today(self):
        return self.__today

    @property
    def most_recent(self):
        return self.__most_recent

    @property
    def increase_from_seven_days_before(self):
        return self.__increase_from_seven_days_before

    @property
    def this_week_per(self):
        return self.__this_week_per

    @property
    def increase_from_last_week_per(self):
        return self.__increase_from_last_week_per

    @property
    def reservation_status_updated(self):
        return self.__reservation_status_updated

    @property
    def first_reservation_status_updated(self):
        return self.__first_reservation_status_updated

    @property
    def child_reservation_status_updated(self):
        return self.__child_reservation_status_updated

    @staticmethod
    def _get_today() -> date:
        """グラフの基準となる最新の報道発表日の日付を返す

        Returns:
            today (date): 最新の報道発表日の日付データ

        """
        now = datetime.now(timezone(timedelta(hours=+9), "JST"))
        try:
            press_release_link_service = PressReleaseLinkService()
            today = press_release_link_service.get_latest_publication_date()
        except DatabaseConnectionError:
            # エラーが起きた場合現在日付を基準とする。
            # このとき市の発表が16時になることが多いので16時より前なら前日を基準とする。
            today = now.date()
            if now.hour < 16:
                today = today - relativedelta(days=1)

        return today

    def _get_aggregate_by_days(self, from_date: date, to_date: date) -> list:
        """PatientsNumberService.get_aggregate_by_days()のラッパー

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            aggregate_by_days (list of tuple): 集計結果
                1日ごとの日付とその週の新規陽性患者数を要素とするタプルのリスト

        """
        service = PatientsNumberService()
        return service.get_aggregate_by_days(from_date=from_date, to_date=to_date)

    def _get_per_hundred_thousand_population_per_week(self, from_date: date, to_date: date) -> list:
        """PatientsNumberService.get_per_hundred_thousand_population_per_weekのラッパー

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            per_hundred_thousand (list of tuple): 集計結果
                1週間ごとの日付とその週の人口10万人あたり新規陽性患者数を要素とするタプルのリスト
        """
        service = PatientsNumberService()
        return service.get_per_hundred_thousand_population_per_week(from_date=from_date, to_date=to_date)

    def get_last_modified(self) -> str:
        """HTTP Last Modifiedヘッダー用文字列を出力

        ATOM FeedとRSS Feed用に最終更新日をHTTP Headerに出力させるため、
        最終更新日を文字列で出力する。時刻は旭川市公式ホームページの発表に合わせて
        16時固定とする。

        Returns:
            last_modified (str): 最終更新日の文字列

        """
        last_modified_date = self._get_today()
        # 時刻は16時固定とするが、UTCとしたいので7時とする
        last_modified_time = time(7, 0, 0, tzinfo=timezone.utc)
        last_modified = datetime.combine(last_modified_date, last_modified_time)

        return last_modified.astimezone(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

    @staticmethod
    def _get_reservation_status_updated() -> datetime:
        """新型コロナワクチン3回目接種予約受付状況テーブルの最終更新日を返す

        Returns:
            updated (datetime): 予約受付状況テーブルの最終更新日

        """
        service = ReservationStatusService()
        return service.get_last_updated()

    @staticmethod
    def _get_first_reservation_status_updated() -> datetime:
        """新型コロナワクチン1・2回目接種予約受付状況テーブルの最終更新日を返す

        Returns:
            updated (datetime): 予約受付状況テーブルの最終更新日

        """
        service = FirstReservationStatusService()
        return service.get_last_updated()

    @staticmethod
    def _get_child_reservation_status_updated() -> datetime:
        """新型コロナワクチン5～11歳接種予約受付状況テーブルの最終更新日を返す

        Returns:
            updated (datetime): 予約受付状況テーブルの最終更新日

        """
        service = ChildReservationStatusService()
        return service.get_last_updated()

    def get_feed(self):
        pass


class RssView(XmlView):
    def __init__(self):
        XmlView.__init__(self)

    def get_feed(self) -> str:
        """RSS Feed文字列を返す

        Returns:
            feed (str): Atom Feed文字列

        """
        title = self.today.strftime("%Y/%m/%d (%a)") + " の旭川市内感染状況の最新動向"
        summary = (
            self.today.strftime("%Y/%m/%d (%a)")
            + " の旭川市の新型コロナ新規感染者数は"
            + self.most_recent
            + "人で、先週の同じ曜日から"
            + self.increase_from_seven_days_before
            + "人でした。"
            + "直近1週間の人口10万人あたりの新規感染者数は"
            + self.this_week_per
            + "人で、先週から"
            + self.increase_from_last_week_per
            + "人となっています。"
        )
        last_modified = self.get_last_modified()
        reservation_status_updated = self.reservation_status_updated.astimezone(timezone.utc)
        first_reservation_status_updated = self.first_reservation_status_updated.astimezone(timezone.utc)
        child_reservation_status_updated = self.child_reservation_status_updated.astimezone(timezone.utc)
        return (
            "<?xml version='1.0' encoding='UTF-8'?>\n"
            + "<rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom'>\n"
            + "  <channel>\n"
            + "    <title>旭川市新型コロナウイルスまとめサイト</title>\n"
            + "    <link>https://"
            + Config.MY_DOMAIN
            + "/</link>\n"
            + "    <description>\n"
            + "旭川市の新型コロナウイルス感染症新規感染者数などの情報を集計して"
            + "グラフとデータで公開しています。"
            + "また、新型コロナワクチン接種医療機関を地図から探せるページも"
            + "公開しています。\n"
            + "    </description>\n"
            + "    <pubDate>"
            + last_modified
            + "</pubDate>\n"
            + "    <lastBuildDate>"
            + last_modified
            + "</lastBuildDate>\n"
            + "    <docs>"
            + "https://"
            + Config.MY_DOMAIN
            + "/rss.xml"
            + "</docs>\n"
            + "  <atom:link rel='self' type='application/rss+xml' href='https://"
            + Config.MY_DOMAIN
            + "/rss.xml' />\n"
            + "    <item>\n"
            + "      <title>"
            + title
            + "</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/</link>\n"
            + "      <description>"
            + summary
            + "</description>\n"
            + "      <pubDate>"
            + last_modified
            + "</pubDate>\n"
            + "      <guid isPermaLink='false'>tag:"
            + Config.MY_DOMAIN
            + ","
            + self.today.strftime("%Y-%m-%d")
            + ":/</guid>\n"
            + "    </item>\n"
            + "    <item>\n"
            + "      <title>このサイトについて</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/about</link>\n"
            + "      <description>旭川市新型コロナウイルスまとめサイトについてのページです。</description>\n"
            + "      <pubDate>Sun, 27 Feb 2022 07:00:00 GMT</pubDate>\n"
            + "      <guid>https://"
            + Config.MY_DOMAIN
            + "/about</guid>\n"
            + "    </item>\n"
            + "    <item>\n"
            + "      <title>ワクチン3回目接種医療機関マップ</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/reservation_statuses</link>\n"
            + "      <description>地図などから新型コロナワクチン3回目接種医療機関の予約受付状況を確認できます。</description>\n"
            + "      <pubDate>"
            + reservation_status_updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
            + "</pubDate>\n"
            + "      <guid>https://"
            + Config.MY_DOMAIN
            + "/reservation_statuses</guid>\n"
            + "    </item>\n"
            + "    <item>\n"
            + "      <title>ワクチン1・2回目接種医療機関マップ</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/first_reservation_statuses</link>\n"
            + "      <description>地図などから新型コロナワクチン1・2回目接種医療機関の予約受付状況を確認できます。</description>\n"
            + "      <pubDate>"
            + first_reservation_status_updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
            + "</pubDate>\n"
            + "      <guid>https://"
            + Config.MY_DOMAIN
            + "/first_reservation_statuses</guid>\n"
            + "    </item>\n"
            + "    <item>\n"
            + "      <title>ワクチン5～11歳接種医療機関マップ</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/child_reservation_statuses</link>\n"
            + "      <description>地図などから新型コロナワクチン5～11歳接種医療機関の予約受付状況を確認できます。</description>\n"
            + "      <pubDate>"
            + child_reservation_status_updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
            + "</pubDate>\n"
            + "      <guid>https://"
            + Config.MY_DOMAIN
            + "/child_reservation_statuses</guid>\n"
            + "    </item>\n"
            + "    <item>\n"
            + "      <title>非公式オープンデータ</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/opendata</link>\n"
            + "      <description>旭川市公式ホームページからスクレイピングして新型コロナウイルス感染症の情報を取得し、"
            + "非公式のオープンデータ（陽性患者属性CSV）としてダウンロードできるようにしたものです。</description>\n"
            + "      <pubDate>"
            + last_modified
            + "</pubDate>\n"
            + "      <guid>https://"
            + Config.MY_DOMAIN
            + "/opendata</guid>\n"
            + "    </item>\n"
            + "    <item>\n"
            + "      <title>感染者の状況</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/patients</link>\n"
            + "      <description>旭川市の新型コロナウイルス感染症患者の状況です。"
            + "2022年1月27日発表分をもって旭川市が感染者ごとの情報の公表をやめたため、同日時点までの情報を表示しています。"
            + "</description>\n"
            + "      <pubDate>Thu, 27 Jan 2022 07:00:00 GMT</pubDate>\n"
            + "      <guid>https://"
            + Config.MY_DOMAIN
            + "/patients</guid>\n"
            + "    </item>\n"
            + "  </channel>\n"
            + "</rss>\n"
        )


class AtomView(XmlView):
    def __init__(self):
        XmlView.__init__(self)

    def get_feed(self) -> str:
        """ATOM Feed文字列を返す

        Returns:
            feed (str): Atom Feed文字列

        """
        title = self.today.strftime("%Y/%m/%d (%a)") + " の旭川市内感染状況の最新動向"
        summary = (
            self.today.strftime("%Y/%m/%d (%a)")
            + " の旭川市の新型コロナ新規感染者数は"
            + self.most_recent
            + "人で、先週の同じ曜日から"
            + self.increase_from_seven_days_before
            + "人でした。"
            + "直近1週間の人口10万人あたりの新規感染者数は"
            + self.this_week_per
            + "人で、先週から"
            + self.increase_from_last_week_per
            + "人となっています。"
        )
        return (
            "<?xml version='1.0' encoding='UTF-8'?>\n"
            + "<feed xmlns='http://www.w3.org/2005/Atom' xml:lang='ja'>\n"
            + "  <id>https://"
            + Config.MY_DOMAIN
            + "/</id>\n"
            + "  <title>旭川市新型コロナウイルスまとめサイト</title>\n"
            + "  <author>\n"
            + "    <name>takedah</name>\n"
            + "    <uri>https://github.com/takedah/ash_unofficial_covid19</uri>\n"
            + "  </author>\n"
            + "  <updated>"
            + self.today.strftime("%Y-%m-%dT16:00:00+09:00")
            + "</updated>\n"
            + "  <link href='https://"
            + Config.MY_DOMAIN
            + "/' />\n"
            + "  <link rel='self' type='application/atom+xml' href='https://"
            + Config.MY_DOMAIN
            + "/atom.xml' />\n"
            + "  <entry>\n"
            + "    <title>"
            + title
            + "</title>\n"
            + "    <link href='https://"
            + Config.MY_DOMAIN
            + "/' />\n"
            + "    <id>tag:"
            + Config.MY_DOMAIN
            + ","
            + self.today.strftime("%Y-%m-%d")
            + ":/</id>\n"
            + "    <updated>"
            + self.today.strftime("%Y-%m-%dT16:00:00+09:00")
            + "</updated>\n"
            + "    <summary>"
            + summary
            + "</summary>\n"
            + "</entry>\n"
            + "  <entry>\n"
            + "    <title>このサイトについて</title>\n"
            + "    <link href='https://"
            + Config.MY_DOMAIN
            + "/about' />\n"
            + "    <id>https://"
            + Config.MY_DOMAIN
            + "/about</id>\n"
            + "    <updated>2022-02-27T16:00:00+09:00</updated>\n"
            + "    <summary>旭川市新型コロナウイルスまとめサイトについてのページです。</summary>\n"
            + "  </entry>\n"
            + "  <entry>\n"
            + "    <title>ワクチン3回目接種医療機関マップ</title>\n"
            + "    <link href='https://"
            + Config.MY_DOMAIN
            + "/reservation_statuses' />\n"
            + "    <id>https://"
            + Config.MY_DOMAIN
            + "/reservation_statuses</id>\n"
            + "    <updated>"
            + self.reservation_status_updated.strftime("%Y-%m-%dT%H:%M:%S+09:00")
            + "</updated>\n"
            + "    <summary>地図などから新型コロナワクチン3回目接種医療機関の予約受付状況を確認できます。</summary>\n"
            + "  </entry>\n"
            + "  <entry>\n"
            + "    <title>ワクチン1・2回目接種医療機関マップ</title>\n"
            + "    <link href='https://"
            + Config.MY_DOMAIN
            + "/first_reservation_statuses' />\n"
            + "    <id>https://"
            + Config.MY_DOMAIN
            + "/first_reservation_statuses</id>\n"
            + "    <updated>"
            + self.first_reservation_status_updated.strftime("%Y-%m-%dT%H:%M:%S+09:00")
            + "</updated>\n"
            + "    <summary>地図などから新型コロナワクチン1・2回目接種医療機関の予約受付状況を確認できます。</summary>\n"
            + "  </entry>\n"
            + "  <entry>\n"
            + "    <title>ワクチン5～11歳接種医療機関マップ</title>\n"
            + "    <link href='https://"
            + Config.MY_DOMAIN
            + "/child_reservation_statuses' />\n"
            + "    <id>https://"
            + Config.MY_DOMAIN
            + "/child_reservation_statuses</id>\n"
            + "    <updated>"
            + self.child_reservation_status_updated.strftime("%Y-%m-%dT%H:%M:%S+09:00")
            + "</updated>\n"
            + "    <summary>地図などから新型コロナワクチン5～11歳接種医療機関の予約受付状況を確認できます。</summary>\n"
            + "  </entry>\n"
            + "  <entry>\n"
            + "    <title>非公式オープンデータ</title>\n"
            + "    <link href='https://"
            + Config.MY_DOMAIN
            + "/opendata' />\n"
            + "    <id>https://"
            + Config.MY_DOMAIN
            + "/opendata</id>\n"
            + "    <updated>"
            + self.today.strftime("%Y-%m-%dT16:00:00+09:00")
            + "</updated>\n"
            + "    <summary>旭川市公式ホームページからスクレイピングして新型コロナウイルス感染症の情報を取得し、"
            + "非公式のオープンデータ（陽性患者属性CSV）としてダウンロードできるようにしたものです。</summary>\n"
            + "  </entry>\n"
            + "  <entry>\n"
            + "    <title>感染者の状況</title>\n"
            + "    <link href='https://"
            + Config.MY_DOMAIN
            + "/patients' />\n"
            + "    <id>https://"
            + Config.MY_DOMAIN
            + "/patients</id>\n"
            + "    <updated>2022-01-27T16:00:00+09:00</updated>\n"
            + "    <summary>旭川市の新型コロナウイルス感染症患者の状況です。"
            + "2022年1月27日発表分をもって旭川市が感染者ごとの情報の公表をやめたため、同日時点までの情報を表示しています。"
            + "</summary>\n"
            + "  </entry>\n"
            + "</feed>\n"
        )
