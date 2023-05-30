import urllib.parse
from datetime import datetime
from typing import Optional

from ..errors import DataModelError, ViewError
from ..models.outpatient import OutpatientLocationFactory
from ..models.point import PointFactory
from ..services.database import ConnectionPool
from ..services.location import LocationService
from ..services.outpatient import OutpatientService
from ..views.view import View


class OutpatientView(View):
    """旭川市新型コロナ発熱外来データ

    旭川市新型コロナ発熱外来データをFlaskへ渡すデータにする

    """

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        self.__service = OutpatientService(pool)

    def get_last_updated(self) -> datetime:
        """
        Returns:
            last_updated (datetime.datetime): 最終更新日

        """
        return self.__service.get_last_updated()

    def find(
        self,
        medical_institution_name: Optional[str] = None,
        is_pediatrics: Optional[bool] = None,
        is_target_not_family: Optional[bool] = None,
    ) -> OutpatientLocationFactory:
        """新型コロナ発熱外来と位置情報の検索

        指定した新型コロナ発熱外来と位置情報を返す

        Args:
            medical_institution_name (str): 医療機関の名称
            is_pediatrics (bool): 小児対応かどうか
            is_target_not_family (bool): かかりつけ患者以外の診療の可否

        Returns:
            results (:obj:`OutpatientLocationFactory`): 発熱外来詳細データ
                新型コロナ発熱外来の情報に緯度経度を含めた
                データオブジェクトのリストを要素に持つオブジェクト。

        """
        return self.__service.find(medical_institution_name, is_pediatrics, is_target_not_family)

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

    def search_by_gps(self, longitude: float, latitude: float) -> list:
        """指定した緯度経度から直線距離が近い上位5件の発熱外来データを返す

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

        outpatients = self.__service.find()
        return LocationService.get_near_locations(locations=outpatients, current_point=current_point)
