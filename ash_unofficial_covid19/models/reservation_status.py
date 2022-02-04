import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

from ..models.factory import Factory


@dataclass()
class ReservationStatus:
    """新型コロナワクチン接種医療機関予約受付状況を表すモデルオブジェクト

    Attributes:
        medical_institution_name (str): 医療機関の名称
        vaccine (str): ワクチンの種類
        area (str): 地区
        address (str): 住所
        phone_number (str): 電話番号
        status (str): 予約受付状況または受付開始時期
        inoculation_time (str): 接種期間・時期
        target_age (str): 対象年齢
        is_target_family (bool): かかりつけの方が対象か
        is_target_not_family (bool): かかりつけ以外の方が対象か
        target_other (str): その他
        memo (str): 備考

    """

    medical_institution_name: str
    vaccine: str
    area: str = ""
    address: str = ""
    phone_number: str = ""
    status: str = ""
    inoculation_time: str = ""
    target_age: str = ""
    is_target_family: Optional[bool] = None
    is_target_not_family: Optional[bool] = None
    target_other: str = ""
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
        vaccine (str): ワクチンの種類
        latitude (float): 医療機関のある緯度
        longitude (float): 医療機関のある経度
        area (str): 地区
        address (str): 住所
        phone_number (str): 電話番号
        status (str): 予約受付状況または受付開始時期
        inoculation_time (str): 接種期間・時期
        target_age (str): 対象年齢
        is_target_family (bool): かかりつけの方が対象か
        is_target_not_family (bool): かかりつけ以外の方が対象か
        target_other (str): その他
        memo (str): 備考
        medical_institution_name_url (str): 医療機関の名称をURLパースした文字列
        area_url (str): 地区をURLパースした文字列

    """

    latitude: float = 0
    longitude: float = 0
    medical_institution_name_url: str = field(init=False)
    area_url: str = field(init=False)

    def __post_init__(self):
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


@dataclass()
class Area:
    """新型コロナワクチン接種医療機関の地区データモデル

    新型コロナワクチン接種医療機関の地区名称とこれをURLパースした文字列を要素に持つ
    データモデル。

    Attributes:
        name (str): 地区名称
        url (str): 地区をURLパースした文字列

    """

    name: str = ""
    url: str = field(init=False)

    def __post_init__(self):
        self.url = urllib.parse.quote(self.name)


class AreaFactory(Factory):
    """新型コロナワクチン接種医療機関の地区データオブジェクトを生成

    Attributes:
        items (list of :obj:`Area`): 医療機関の地区データリスト
            Areaクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> Area:
        """Areaオブジェクトの生成

        Args:
            row (dict): 医療機関の地区データの辞書
                新型コロナワクチン接種医療機関の地区データオブジェクトを
                作成するための引数

        Returns:
            item (:obj:`Area`): 医療機関の地区データ
                Areaクラスのオブジェクト

        """
        return Area(**row)

    def _register_item(self, item: Area):
        """Areaオブジェクトをリストへ追加

        Args:
            item (:obj:`Area`): データオブジェクト
                Areaクラスのオブジェクト

        """
        self.__items.append(item)
