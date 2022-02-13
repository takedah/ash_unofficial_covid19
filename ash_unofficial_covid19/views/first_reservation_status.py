from typing import Optional

from ..models.first_reservation_status import FirstReservationStatusLocationFactory
from ..models.reservation_status import AreaFactory
from ..services.first_reservation_status import FirstReservationStatusService
from ..views.view import View


class FirstReservationStatusView(View):
    """旭川市新型コロナワクチン1・2回目接種医療機関予約受付状況データ

    旭川市新型コロナワクチン1・2回目接種医療機関予約受付状況データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = FirstReservationStatusService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self):
        return self.__last_updated

    def find(
        self, medical_institution_name: Optional[str] = None, area: Optional[str] = None
    ) -> FirstReservationStatusLocationFactory:
        """新型コロナワクチン1・2回目接種医療機関予約状況と位置情報の検索

        指定した新型コロナワクチン1・2回目接種医療機関の予約受付状況と位置情報を返す

        Args:
            medical_institution_name (str): 医療機関の名称
            area (str): 地区

        Returns:
            results (:obj:`FirstReservationStatusLocationFactory`): 予約受付状況詳細データ
                新型コロナワクチン1・2回目接種医療機関予約受付状況の情報に緯度経度を含めた
                データオブジェクトのリストを要素に持つオブジェクト。

        """
        return self.__service.find(medical_institution_name, area)

    def get_areas(self) -> AreaFactory:
        """新型コロナワクチン1・2回目接種医療機関の地区名称とこれをURLパースした文字列一覧を取得

        新型コロナワクチン1・2回目接種医療機関の地区名称とこれをURLパースした文字列を要素に持つ
        オブジェクトを返す。

        Returns:
            areas (:obj:`AreaFactory`): 医療機関の地区・URLパース文字列一覧データ
                新型コロナワクチン1・2回目接種医療機関の地区名称とこれをURLパースした文字列
                データオブジェクトのリストを要素に持つオブジェクトを返す。

        """
        return self.__service.get_areas()

    def get_reservation_status_json(self) -> str:
        """新型コロナワクチン1・2回目接種医療機関予約受付状況のJSON文字列データを返す

        Returns:
            json_data (str): 医療機関予約受付状況JSONファイルの文字列データ

        """
        json_data = self.__service.get_dicts()
        return self.dict_to_json(json_data)
