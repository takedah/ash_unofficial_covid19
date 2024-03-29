import urllib.parse
from datetime import datetime
from typing import Optional

from ..errors import DataModelError, ViewError
from ..models.point import PointFactory
from ..models.reservation_status import ReservationStatusLocationFactory
from ..services.database import ConnectionPool
from ..services.location import LocationService
from ..services.reservation_status import ReservationStatusService
from ..views.view import View


class ReservationStatusView(View):
    """旭川市新型コロナワクチン接種医療機関予約受付状況データ

    旭川市新型コロナワクチン接種医療機関予約受付状況データをFlaskへ渡すデータにする

    """

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        self.__service = ReservationStatusService(pool)

    def get_last_updated(self) -> datetime:
        """
        Returns:
            last_updated (datetime.datetime): 最終更新日

        """
        return self.__service.get_last_updated()

    def find(
        self,
        medical_institution_name: Optional[str] = None,
        area: Optional[str] = None,
        division: Optional[str] = None,
    ) -> ReservationStatusLocationFactory:
        """新型コロナワクチン接種医療機関予約状況と位置情報の検索

        指定した新型コロナワクチン接種医療機関の予約受付状況と位置情報を返す

        Args:
            medical_institution_name (str): 医療機関の名称
            area (str): 地区
            division (str): 接種種別

        Returns:
            results (:obj:`ReservationStatusLocationFactory`): 予約受付状況詳細データ
                新型コロナワクチン接種医療機関予約受付状況の情報に緯度経度を含めた
                データオブジェクトのリストを要素に持つオブジェクト。

        """
        return self.__service.find(medical_institution_name, area, division)

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

    def get_division_list(self) -> list:
        """新型コロナワクチン接種医療機関の接種種別名称とこれをURLパースした文字列一覧を取得

        新型コロナワクチン接種医療機関の接種種別名称とこれをURLパースした文字列を要素に持つ
        辞書のリストを返す。

        Returns:
            division_list (list of dict): 医療機関の接種種別・URLパース文字列一覧データ

        """
        division_list = list()
        division_names = self.__service.get_division_list()
        for division_name in division_names:
            division_list.append(
                {
                    "name": division_name,
                    "url": urllib.parse.quote(division_name),
                }
            )
        return division_list

    def get_medical_institution_list(self) -> list:
        """新型コロナワクチン接種医療機関名とこれをURLパースした文字列一覧を取得

        新型コロナワクチン接種医療機関名とこれをURLパースした文字列を要素に持つ
        辞書のリストを返す。

        Returns:
            medical_institution_list (list of dict): 医療機関名・URLパース文字列一覧データ

        """
        # 元のリストが医療機関名と接種種別、ワクチンのタプルが要素となっているため、
        # 医療機関名のみ抽出して重複を削除しておく。
        medical_institution_name_vaccine_list = self.__service.get_medical_institution_list()
        medical_institution_names = list()
        for medical_institution_name in medical_institution_name_vaccine_list:
            medical_institution_names.append(medical_institution_name[0])

        medical_institution_names = sorted(set(medical_institution_names), key=medical_institution_names.index)

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
        """新型コロナワクチン接種医療機関予約受付状況のJSON文字列データを返す

        Returns:
            json_data (str): 医療機関予約受付状況JSONファイルの文字列データ

        """
        json_data = self.__service.get_dicts()
        return self.dict_to_json(json_data)

    def search_by_gps(self, longitude: float, latitude: float, division: str) -> list:
        """指定した緯度経度から直線距離が近い上位5件の医療機関予約受付状況データを返す

        Args:
            longitude (float): 経度
            latitude (float): 緯度
            division (str): 接種種別

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

        reservation_statuses = self.__service.find(division=division)
        return LocationService.get_near_locations(locations=reservation_statuses, current_point=current_point)
