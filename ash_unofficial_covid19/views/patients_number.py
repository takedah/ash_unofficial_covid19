from datetime import date, datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from ..errors import DatabaseConnectionError
from ..services.patients_number import PatientsNumberService
from ..services.press_release_link import PressReleaseLinkService
from ..views.view import View


class PatientsNumberView(View):
    """旭川市新型コロナウイルス感染症陽性患者数データ

    旭川市新型コロナウイルス感染症陽性患者数データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = PatientsNumberService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self):
        return self.__last_updated

    @staticmethod
    def get_today() -> date:
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

    def get_daily_total_csv(self) -> str:
        """陽性患者日計CSVファイルの文字列データを返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            csv_data (str): 陽性患者日計CSVファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        to_date = self.get_today()
        csv_data = self.__service.get_aggregate_by_days(from_date=from_date, to_date=to_date)
        csv_data.insert(
            0,
            [
                "公表日",
                "陽性患者数",
            ],
        )
        return self.list_to_csv(csv_data)

    def get_daily_total_json(self) -> str:
        """陽性患者日計JSONファイルの文字列データを返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            json_data (str): 陽性患者日計JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        to_date = self.get_today()
        aggregate_by_days = self.__service.get_aggregate_by_days(from_date=from_date, to_date=to_date)
        json_data = dict((d.strftime("%Y-%m-%d"), n) for d, n in aggregate_by_days)
        return self.dict_to_json(json_data)

    def get_daily_total_per_age_json(self) -> str:
        """陽性患者年代別日計JSONファイルの文字列データを返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            json_data (str): 日別年代別陽性患者数JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        to_date = self.get_today()
        json_data = self.__service.get_dicts(from_date=from_date, to_date=to_date)
        return self.dict_to_json(json_data)
