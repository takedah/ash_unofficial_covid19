from datetime import date

from ..services.patients_number import PatientsNumberService
from ..views.view import View


class PatientsNumberView(View):
    """旭川市新型コロナウイルス感染症陽性患者数データ

    旭川市新型コロナウイルス感染症陽性患者数データをFlaskへ渡すデータにする

    Attributes:
        today (date): データを作成する基準日
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): データを作成する基準日

        """
        self.__service = PatientsNumberService()
        self.__today = today
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self):
        return self.__last_updated

    def get_daily_total_csv(self) -> str:
        """陽性患者日計CSVファイルの文字列データを返す

        Returns:
            csv_data (str): 陽性患者日計CSVファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        csv_data = self.__service.get_aggregate_by_days(from_date=from_date, to_date=self.__today)
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

        Returns:
            json_data (str): 陽性患者日計JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        aggregate_by_days = self.__service.get_aggregate_by_days(from_date=from_date, to_date=self.__today)
        json_data = dict((d.strftime("%Y-%m-%d"), n) for d, n in aggregate_by_days)
        return self.dict_to_json(json_data)

    def get_daily_total_per_age_csv(self) -> str:
        """陽性患者年代別日計CSVファイルの文字列データを返す

        Returns:
            json_data (str): 日別年代別陽性患者数JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        csv_data = self.__service.get_lists(from_date=from_date, to_date=self.__today)
        csv_data.insert(
            0,
            ["公表日", "10歳未満", "10代", "20代", "30代", "40代", "50代", "60代", "70代", "80代", "90歳以上", "調査中等"],
        )
        return self.list_to_csv(csv_data)

    def get_daily_total_per_age_json(self) -> str:
        """陽性患者年代別日計JSONファイルの文字列データを返す

        Returns:
            json_data (str): 日別年代別陽性患者数JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        json_data = self.__service.get_dicts(from_date=from_date, to_date=self.__today)
        return self.dict_to_json(json_data)
