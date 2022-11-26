import urllib.parse
from datetime import datetime
from typing import Optional

from ..errors import DataModelError, ViewError
from ..models.first_reservation_status import FirstReservationStatusLocationFactory
from ..models.point import PointFactory
from ..services.first_reservation_status import FirstReservationStatusService
from ..services.location import LocationService
from ..views.view import View


class FirstReservationStatusView(View):
    """旭川市新型コロナワクチン1・2回目接種医療機関予約受付状況データ

    旭川市新型コロナワクチン1・2回目接種医療機関予約受付状況データをFlaskへ渡すデータにする

    """

    def __init__(self):
        self.__service = FirstReservationStatusService()

    def get_last_updated(self) -> datetime:
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (datetime.datetime): 最終更新日

        """
        return self.__service.get_last_updated()

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

    def get_area_list(self) -> list:
        """新型コロナワクチン接種医療機関の地区名称とこれをURLパースした文字列一覧を取得

        新型コロナワクチン接種医療機関の地区名称とこれをURLパースした文字列を要素に持つ
        辞書のリストを返す。

        Returns:
            area_list (list of dict): 医療機関の地区・URLパース文字列一覧データ

        """
        area_list = list()
        area_names = self.__service.get_area_list()
        for area_name in area_names:
            area_list.append(
                {
                    "name": area_name,
                    "url": urllib.parse.quote(area_name),
                }
            )
        return area_list

    def get_medical_institution_list(self) -> list:
        """新型コロナワクチン接種医療機関名とこれをURLパースした文字列一覧を取得

        新型コロナワクチン接種医療機関名とこれをURLパースした文字列を要素に持つ
        辞書のリストを返す。

        Returns:
            medical_institution_list (list of dict): 医療機関名・URLパース文字列一覧データ

        """
        medical_institution_names = self.__service.get_medical_institution_list()
        medical_institution_list = list()
        for medical_institution_name in medical_institution_names:
            medical_institution_list.append(
                {
                    "name": medical_institution_name,
                    "url": urllib.parse.quote(medical_institution_name),
                }
            )
        return medical_institution_list

    def get_reservation_status_json(self) -> str:
        """新型コロナワクチン1・2回目接種医療機関予約受付状況のJSON文字列データを返す

        Returns:
            json_data (str): 医療機関予約受付状況JSONファイルの文字列データ

        """
        json_data = self.__service.get_dicts()
        return self.dict_to_json(json_data)

    def search_by_gps(self, longitude: float, latitude: float) -> list:
        """指定した緯度経度から直線距離が近い上位5件の医療機関予約受付状況データを返す

        Args:
            longitude (float): 経度
            latitude (float): 緯度

        Returns:
            near_locations (list of dicts): 現在地から最も近い上位5件の
                医療機関オブジェクトと順位、現在地までの距離（キロメートルに換算し
                小数点第3位を切り上げ）を要素に持つ辞書のリスト

        """
        point_factory = PointFactory()
        try:
            current_point = point_factory.create(longitude=longitude, latitude=latitude)
        except DataModelError as e:
            raise ViewError(e.message)

        reservation_statuses = self.__service.find()
        return LocationService.get_near_locations(locations=reservation_statuses, current_point=current_point)
