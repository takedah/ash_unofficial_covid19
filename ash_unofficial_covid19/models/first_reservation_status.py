from dataclasses import dataclass
from typing import Optional

from ..models.factory import Factory
from ..models.reservation_status import ReservationStatus, ReservationStatusLocation


@dataclass()
class FirstReservationStatus(ReservationStatus):
    """新型コロナワクチン1・2回目接種医療機関予約受付状況を表すモデルオブジェクト

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
        is_target_suberb (bool): 市外の方が対象か
        target_other (str): その他
        memo (str): 備考

    """

    vaccine: Optional[str] = None
    is_target_suberb: Optional[bool] = None


class FirstReservationStatusFactory(Factory):
    """新型コロナワクチン1・2回目接種医療機関の予約受付状況を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`FirstReservationStatus`): 医療機関予約受付状況一覧リスト
            FirstReservationStatusクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> FirstReservationStatus:
        """FirstReservationStatusオブジェクトの生成

        Args:
            row (dict): 医療機関予約受付状況データの辞書
                新型コロナワクチン接種医療機関予約受付状況データオブジェクトを
                作成するための引数

        Returns:
            reservation_status (:obj:`FirstReservationStatus`): 医療機関予約受付状況データ
                FirstReservationStatusクラスのオブジェクト

        """
        return FirstReservationStatus(**row)

    def _register_item(self, item: FirstReservationStatus):
        """FirstReservationStatusオブジェクトをリストへ追加

        Args:
            item (:obj:`FirstReservationStatus`): FirstReservationStatusクラスのオブジェクト

        """
        self.__items.append(item)


@dataclass()
class FirstReservationStatusLocation(ReservationStatusLocation):
    """新型コロナワクチン1・2回目接種医療機関予約受付状況詳細データモデル

    新型コロナワクチン1・2回目接種医療機関予約受付状況に位置情報を加えたデータモデル。

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
        is_target_suberb (bool): 市外の方が対象か
        target_other (str): その他
        memo (str): 備考
        medical_institution_name_url (str): 医療機関の名称をURLパースした文字列
        area_url (str): 地区をURLパースした文字列

    """

    vaccine: Optional[str] = None
    is_target_suberb: Optional[bool] = None


class FirstReservationStatusLocationFactory(Factory):
    """新型コロナワクチン1・2回目接種医療機関予約受付状況詳細オブジェクトを生成

    Attributes:
        items (list of :obj:`FirstReservationStatusLocation`): 医療機関予約受付状況詳細リスト
            FirstReservationStatusLocationクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> FirstReservationStatusLocation:
        """FirstReservationStatusLocationオブジェクトの生成

        Args:
            row (dict): 医療機関予約受付状況詳細データの辞書
                新型コロナワクチン1・2回目接種医療機関予約受付状況詳細データオブジェクトを
                作成するための引数

        Returns:
            item (:obj:`FirstReservationStatusLocation`): 医療機関予約受付状況詳細データ
                FirstReservationStatusLocationクラスのオブジェクト

        """
        return FirstReservationStatusLocation(**row)

    def _register_item(self, item: FirstReservationStatusLocation):
        """FirstReservationStatusLocationオブジェクトをリストへ追加

        Args:
            item (:obj:`FirstReservationStatusLocation`): データオブジェクト
                FirstReservationStatusLocationクラスのオブジェクト

        """
        self.__items.append(item)
