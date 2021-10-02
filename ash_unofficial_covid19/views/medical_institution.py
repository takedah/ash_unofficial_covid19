import urllib.parse
from io import StringIO
from typing import Optional

from ..models.medical_institution_location_reservation_status import MedicalInstitutionLocationReservationStatus
from ..services.medical_institution import MedicalInstitutionService
from ..services.medical_institution_location import MedicalInstitutionLocationService
from ..services.medical_institution_location_reservation_status import (
    MedicalInstitutionLocationReservationStatusService,
)


class MedicalInstitutionsView:
    """旭川市新型コロナワクチン接種医療機関データ

    旭川市新型コロナワクチン接種医療機関データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = MedicalInstitutionService()
        self.__location_service = MedicalInstitutionLocationService()
        self.__reservation_status_service = MedicalInstitutionLocationReservationStatusService()
        last_updated = self.__service.get_last_updated()
        reservation_status_updated = self.__reservation_status_service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")
        self.__reservation_status_updated = reservation_status_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self) -> str:
        return self.__last_updated

    @property
    def reservation_status_updated(self) -> str:
        return self.__reservation_status_updated

    def find(self, name: str, is_pediatric: bool = False) -> MedicalInstitutionLocationReservationStatus:
        """位置情報、予約受付情報付き新型コロナワクチン接種医療機関情報

        指定した対象年齢の新型コロナワクチン接種医療機関の一覧に医療機関の位置情報と
        予約受付情報を付けて返す

        Args:
            name (str): 医療機関の名称
            target_age (bool): 対象年齢フラグ
                真の場合は対象年齢が12歳から15歳まで、偽の場合16歳以上を表す

        Returns:
            results (:obj:`MedicalInstitutionLocationReservationStatus`): 医療機関データ
                新型コロナワクチン接種医療機関の情報に緯度経度と予約受付情報を含めた
                データオブジェクト

        """
        return self.__reservation_status_service.find(name=name, is_pediatric=is_pediatric)

    def find_area(self, area: Optional[str] = None, is_pediatric: bool = False) -> list:
        """新型コロナワクチン接種医療機関の位置情報一覧

        指定した対象年齢の新型コロナワクチン接種医療機関の一覧に医療機関の位置情報を
        付けて返す

        Args:
            area (str): 医療機関の地区
            target_age (bool): 対象年齢フラグ
                真の場合は対象年齢が12歳から15歳まで、偽の場合16歳以上を表す

        Returns:
            response (list of tuple): 位置情報付き医療機関一覧データ
                新型コロナワクチン接種医療機関の情報に緯度経度を含めたタプルのリスト

        """
        response = list()
        medical_institution_locations = self.__reservation_status_service.find_area(
            area=area, is_pediatric=is_pediatric
        )
        for medical_institution_location in medical_institution_locations.items:
            response.append(
                (
                    medical_institution_location,
                    urllib.parse.quote(medical_institution_location.name),
                )
            )
        return response

    def get_area_list(self, is_pediatric: bool = False) -> list:
        """指定した対象年齢の新型コロナワクチン接種医療機関の地域全件のリストを返す

        Args:
            is_pediatric (bool): 12歳から15歳までの接種医療機関の場合真を指定

        Returns:
            res (list of tuple): 医療機関の地域一覧リスト
                医療機関の地域名称とそれをURLエンコードした文字列と対で返す

        """
        area_list = list()
        for area in self.__service.get_area_list(is_pediatric):
            area_list.append((area, urllib.parse.quote(area)))
        return area_list

    def get_csv(self) -> StringIO:
        """新型コロナワクチン接種医療機関一覧のデータをCSVで返す

        Returns:
            csv_data (StringIO): 新型コロナワクチン接種医療機関一覧のCSVデータ

        """
        csv_rows = self.__service.get_csv_rows()
        return self.__service.get_csv(csv_rows)
