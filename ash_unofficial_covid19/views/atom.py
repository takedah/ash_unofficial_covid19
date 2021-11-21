from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta

from ..config import Config
from ..errors import DatabaseConnectionError
from ..services.patient import AsahikawaPatientService
from ..services.press_release_link import PressReleaseLinkService


class AtomView:
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
        """PatientService.get_aggregate_by_days()のラッパー

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            aggregate_by_days (list of tuple): 集計結果
                1日ごとの日付とその週の新規陽性患者数を要素とするタプルのリスト

        """
        service = AsahikawaPatientService()
        return service.get_aggregate_by_days(from_date=from_date, to_date=to_date)

    def _get_per_hundred_thousand_population_per_week(self, from_date: date, to_date: date) -> list:
        """PatientService.get_per_hundred_thousand_population_per_weekのラッパー

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            per_hundred_thousand (list of tuple): 集計結果
                1週間ごとの日付とその週の人口10万人あたり新規陽性患者数を要素とするタプルのリスト
        """
        service = AsahikawaPatientService()
        return service.get_per_hundred_thousand_population_per_week(from_date=from_date, to_date=to_date)

    def get_feed(self) -> str:
        """Atom Feed文字列を返す

        Returns:
            feed (str): Atom Feed文字列

        """
        summary = (
            self.today.strftime("%Y/%m/%d (%a)")
            + " の旭川市の新型コロナ新規感染者数は"
            + self.most_recent
            + "人で、先週の同じ曜日から"
            + self.increase_from_seven_days_before
            + "人でした。"
            + "直近1週間の人口10万人あたりの新規感染者数は"
            + self.__this_week_per
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
            + "    <title>旭川市内感染状況の最新動向</title>\n"
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
