from typing import Optional

from ..models.factory import Factory


class ReservationStatusLocation:
    """旭川市新型コロナワクチン接種医療機関予約受付状況に位置情報をつけたデータを表すモデルオブジェクト

    Attributes:
        medical_institution_name (str): 医療機関の名称
        address (str): 医療機関の住所
        phone_number (str): 医療機関の電話番号
        status (str): 予約受付状況
        inoculation_time (str): 接種期間・時期
        target_age (str): 対象年齢
        target_family (bool): かかりつけの方が対象か
        target_not_family (bool): かかりつけ以外の方が対象か
        target_suberbs (bool): 市外の方が対象か
        target_other (str): その他
        latitude (float): 医療機関のある緯度
        longitude (float): 医療機関のある経度
        memo (str): 備考

    """

    def __init__(
        self,
        medical_institution_name: str,
        address: str,
        phone_number: str,
        status: Optional[str],
        inoculation_time: Optional[str],
        target_age: str,
        target_family: bool,
        target_not_family: bool,
        target_suberbs: bool,
        target_other: str,
        latitude: float,
        longitude: float,
        memo: str,
    ):
        """
        Args:
            medical_institution_name (str): 医療機関の名称
            address (str): 医療機関の住所
            phone_number (str): 医療機関の電話番号
            status (str): 予約受付状況
            inoculation_time (str): 接種期間・時期
            target_age (str): 対象年齢
            target_family (bool): かかりつけの方が対象か
            target_not_family (bool): かかりつけ以外の方が対象か
            target_suberbs (bool): 市外の方が対象か
            target_other (str): その他
            latitude (float): 医療機関のある緯度
            longitude (float): 医療機関のある経度
            memo (str): 備考

        """
        self.__medical_institution_name = medical_institution_name
        self.__address = address
        self.__phone_number = phone_number
        self.__status = status
        self.__inoculation_time = inoculation_time
        self.__target_age = target_age
        self.__target_family = target_family
        self.__target_not_family = target_not_family
        self.__target_suberbs = target_suberbs
        self.__target_other = target_other
        self.__latitude = latitude
        self.__longitude = longitude
        self.__memo = memo

    @property
    def medical_institution_name(self):
        return self.__medical_institution_name

    @property
    def address(self):
        return self.__address

    @property
    def phone_number(self):
        return self.__phone_number

    @property
    def status(self):
        return self.__status

    @property
    def inoculation_time(self):
        return self.__inoculation_time

    @property
    def target_age(self):
        return self.__target_age

    @property
    def target_family(self):
        return self.__target_family

    @property
    def target_not_family(self):
        return self.__target_not_family

    @property
    def target_suberbs(self):
        return self.__target_suberbs

    @property
    def target_other(self):
        return self.__target_other

    @property
    def longitude(self):
        return self.__longitude

    @property
    def latitude(self):
        return self.__latitude

    @property
    def memo(self):
        return self.__memo


class ReservationStatusLocationFactory(Factory):
    """旭川市新型コロナワクチン接種医療機関を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`ReservationStatusLocation`): 医療機関一覧リスト
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
            row (dict): 医療機関データの辞書
                新型コロナワクチン接種医療機関データオブジェクトを作成するための引数

        Returns:
            item (:obj:`ReservationStatusLocation`): 医療機関データ
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
