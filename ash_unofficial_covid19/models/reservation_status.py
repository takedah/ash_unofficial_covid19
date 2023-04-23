import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

from ..models.factory import Factory


@dataclass()
class ReservationStatus:
    """新型コロナワクチン接種医療機関予約受付状況を表すモデルオブジェクト

    Attributes:
        medical_institution_name (str): 医療機関の名称
        division (str): 接種種類
        vaccine (str): ワクチンの種類
        area (str): 地区
        address (str): 住所
        phone_number (str): 電話番号
        status (str): 受付開始時期
        inoculation_time (str): 接種開始時期
        is_target_family (bool): かかりつけの方が対象か
        is_target_not_family (bool): かかりつけ以外の方が対象か
        is_target_suberb (bool): 市外の方が対象か
        memo (str): 備考

    """

    medical_institution_name: str
    division: str
    vaccine: str
    area: str = ""
    address: str = ""
    phone_number: str = ""
    status: str = ""
    inoculation_time: str = ""
    is_target_family: Optional[bool] = None
    is_target_not_family: Optional[bool] = None
    is_target_suberb: Optional[bool] = None
    memo: str = ""


class ReservationStatusFactory(Factory):
    """新型コロナワクチン接種医療機関の予約受付状況を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`ReservationStatus`): 医療機関予約受付状況一覧リスト
            ReservationStatusクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> ReservationStatus:
        """ReservationStatusオブジェクトの生成

        Args:
            row (dict): 医療機関予約受付状況データの辞書
                新型コロナワクチン接種医療機関予約受付状況データオブジェクトを
                作成するための引数

        Returns:
            reservation_status (:obj:`ReservationStatus`): 医療機関予約受付状況データ
                ReservationStatusクラスのオブジェクト

        """
        return ReservationStatus(**row)

    def _register_item(self, item: ReservationStatus):
        """ReservationStatusオブジェクトをリストへ追加

        Args:
            item (:obj:`ReservationStatus`): ReservationStatusクラスのオブジェクト

        """
        self.__items.append(item)


@dataclass()
class ReservationStatusLocation(ReservationStatus):
    """新型コロナワクチン接種医療機関予約受付状況詳細データモデル

    新型コロナワクチン接種医療機関予約受付状況に位置情報を加えたデータモデル。

    Attributes:
        medical_institution_name (str): 医療機関の名称
        division (str): 接種種類
        vaccine (str): ワクチンの種類
        latitude (float): 医療機関のある緯度
        longitude (float): 医療機関のある経度
        area (str): 地区
        address (str): 住所
        phone_number (str): 電話番号
        status (str): 予約受付開始時期
        inoculation_time (str): 接種開始時期
        is_target_family (bool): かかりつけの方が対象か
        is_target_not_family (bool): かかりつけ以外の方が対象か
        is_target_suberb (bool): 市外の方が対象か
        memo (str): 備考
        division_url (str): 接種種類をURLパースした文字列
        medical_institution_name_url (str): 医療機関の名称をURLパースした文字列
        area_url (str): 地区をURLパースした文字列

    """

    latitude: float = 0
    longitude: float = 0
    division_url: str = field(init=False)
    medical_institution_name_url: str = field(init=False)
    area_url: str = field(init=False)

    def __post_init__(self):
        self.division_url = urllib.parse.quote(self.division)
        self.medical_institution_name_url = urllib.parse.quote(self.medical_institution_name)
        self.area_url = urllib.parse.quote(self.area)


class ReservationStatusLocationFactory(Factory):
    """新型コロナワクチン接種医療機関予約受付状況詳細オブジェクトを生成

    Attributes:
        items (list of :obj:`ReservationStatusLocation`): 医療機関予約受付状況詳細リスト
            ReservationStatusLocationクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> ReservationStatusLocation:
        """ReservationStatusLocationオブジェクトの生成

        Args:
            row (dict): 医療機関予約受付状況詳細データの辞書
                新型コロナワクチン接種医療機関予約受付状況詳細データオブジェクトを
                作成するための引数

        Returns:
            item (:obj:`ReservationStatusLocation`): 医療機関予約受付状況詳細データ
                ReservationStatusLocationクラスのオブジェクト

        """
        return ReservationStatusLocation(**row)

    def _register_item(self, item: ReservationStatusLocation):
        """ReservationStatusLocationオブジェクトをリストへ追加

        Args:
            item (:obj:`ReservationStatusLocation`): データオブジェクト
                ReservationStatusLocationクラスのオブジェクト

        """
        self.__items.append(item)
