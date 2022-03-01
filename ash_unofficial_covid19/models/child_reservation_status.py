from dataclasses import dataclass

from ..models.factory import Factory
from ..models.reservation_status import ReservationStatus, ReservationStatusLocation


@dataclass()
class ChildReservationStatus(ReservationStatus):
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


class ChildReservationStatusFactory(Factory):
    """新型コロナワクチン接種医療機関の予約受付状況を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`ChildReservationStatus`): 医療機関予約受付状況一覧リスト
            ChildReservationStatusクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> ChildReservationStatus:
        """ChildReservationStatusオブジェクトの生成

        Args:
            row (dict): 医療機関予約受付状況データの辞書
                新型コロナワクチン接種医療機関予約受付状況データオブジェクトを
                作成するための引数

        Returns:
            reservation_status (:obj:`ChildReservationStatus`): 医療機関予約受付状況データ
                ChildReservationStatusクラスのオブジェクト

        """
        return ChildReservationStatus(**row)

    def _register_item(self, item: ChildReservationStatus):
        """ChildReservationStatusオブジェクトをリストへ追加

        Args:
            item (:obj:`ChildReservationStatus`): ChildReservationStatusクラスのオブジェクト

        """
        self.__items.append(item)


@dataclass()
class ChildReservationStatusLocation(ReservationStatusLocation):
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


class ChildReservationStatusLocationFactory(Factory):
    """新型コロナワクチン接種医療機関予約受付状況詳細オブジェクトを生成

    Attributes:
        items (list of :obj:`ChildReservationStatusLocation`): 医療機関予約受付状況詳細リスト
            ChildReservationStatusLocationクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> ChildReservationStatusLocation:
        """ChildReservationStatusLocationオブジェクトの生成

        Args:
            row (dict): 医療機関予約受付状況詳細データの辞書
                新型コロナワクチン接種医療機関予約受付状況詳細データオブジェクトを
                作成するための引数

        Returns:
            item (:obj:`ChildReservationStatusLocation`): 医療機関予約受付状況詳細データ
                ChildReservationStatusLocationクラスのオブジェクト

        """
        return ChildReservationStatusLocation(**row)

    def _register_item(self, item: ChildReservationStatusLocation):
        """ChildReservationStatusLocationオブジェクトをリストへ追加

        Args:
            item (:obj:`ChildReservationStatusLocation`): データオブジェクト
                ChildReservationStatusLocationクラスのオブジェクト

        """
        self.__items.append(item)
