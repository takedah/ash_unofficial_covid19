from datetime import date, datetime, time, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta

from ..config import Config
from ..errors import DatabaseConnectionError
from ..services.patients_number import PatientsNumberService
from ..services.press_release_link import PressReleaseLinkService


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
        title = self.today.strftime("%Y/%m/%d (%a)") + "の旭川市内感染状況の最新動向"
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
            + "<rss version='2.0' xmlns:atom='http://www.w3.org/2005/Atom'>\n"
            + "  <channel>\n"
            + "    <atom:link href='https://"
            + Config.MY_DOMAIN
            + "/rss.xml' rel='self' type='application/rss+xml' />\n"
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
            + "    <item>\n"
            + "      <guid isPermaLink='true'>https://"
            + Config.MY_DOMAIN
            + "/</guid>\n"
            + "      <title>"
            + title
            + "</title>\n"
            + "      <link>https://"
            + Config.MY_DOMAIN
            + "/</link>\n"
            + "      <pubDate>"
            + self.today.strftime("%a, %d %b %Y 16:00:00 +0900")
            + "</pubDate>\n"
            + "      <description>"
            + summary
            + "</description>\n"
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
        title = self.today.strftime("%Y/%m/%d (%a)") + "の旭川市内感染状況の最新動向"
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
            + "  <id>tag:"
            + Config.MY_DOMAIN
            + ",2021-02-28:/</id>\n"
            + "  <title>旭川市新型コロナウイルスまとめサイト</title>\n"
            + "  <author>\n"
            + "    <name>takedah</name>\n"
            + "    <uri>https://github.com/takedah/ash_unofficial_covid19</uri>\n"
            + "  </author>\n"
            + "  <updated>"
            + self.today.strftime("%Y-%m-%dT16:00:00+09:00")
            + "</updated>\n"
            + "  <link rel='alternate' type='text/html' href='https://"
            + Config.MY_DOMAIN
            + "/' />\n"
            + "  <link rel='self' type='application/atom+xml' href='https://"
            + Config.MY_DOMAIN
            + "/atom.xml' />\n"
            + "  <entry>\n"
            + "    <id>https://"
            + Config.MY_DOMAIN
            + "/</id>\n"
            + "    <title>"
            + title
            + "</title>\n"
            + "    <link rel='alternate' type='text/html' href='https://"
            + Config.MY_DOMAIN
            + "/' />\n"
            + "    <updated>"
            + self.today.strftime("%Y-%m-%dT16:00:00+09:00")
            + "</updated>\n"
            + "    <summary>"
            + summary
            + "</summary>\n"
            + "  </entry>\n"
            + "</feed>\n"
        )
