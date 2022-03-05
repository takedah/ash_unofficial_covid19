from typing import Optional

from ..models.area import AreaFactory
from ..models.point import PointFactory
from ..models.reservation_status import ReservationStatusLocationFactory
from ..services.location import LocationService
from ..services.reservation_status import ReservationStatusService
from ..views.view import View


class ReservationStatusView(View):
    """旭川市新型コロナワクチン接種医療機関予約受付状況データ

    旭川市新型コロナワクチン接種医療機関予約受付状況データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = ReservationStatusService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self):
        return self.__last_updated

    def find(
        self, medical_institution_name: Optional[str] = None, area: Optional[str] = None
    ) -> ReservationStatusLocationFactory:
        """新型コロナワクチン接種医療機関予約状況と位置情報の検索

        指定した新型コロナワクチン接種医療機関の予約受付状況と位置情報を返す

        Args:
            medical_institution_name (str): 医療機関の名称
            area (str): 地区

        Returns:
            results (:obj:`ReservationStatusLocationFactory`): 予約受付状況詳細データ
                新型コロナワクチン接種医療機関予約受付状況の情報に緯度経度を含めた
                データオブジェクトのリストを要素に持つオブジェクト。

        """
        return self.__service.find(medical_institution_name, area)

    def get_areas(self) -> AreaFactory:
        """新型コロナワクチン接種医療機関の地区名称とこれをURLパースした文字列一覧を取得

        新型コロナワクチン接種医療機関の地区名称とこれをURLパースした文字列を要素に持つ
        オブジェクトを返す。

        Returns:
            areas (:obj:`AreaFactory`): 医療機関の地区・URLパース文字列一覧データ
                新型コロナワクチン接種医療機関の地区名称とこれをURLパースした文字列
                データオブジェクトのリストを要素に持つオブジェクトを返す。

        """
        return self.__service.get_areas()

    def get_reservation_status_json(self) -> str:
        """新型コロナワクチン接種医療機関予約受付状況のJSON文字列データを返す

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
        current_point = point_factory.create(longitude=longitude, latitude=latitude)
        reservation_statuses = self.__service.find()
        return LocationService.get_near_locations(locations=reservation_statuses, current_point=current_point)
