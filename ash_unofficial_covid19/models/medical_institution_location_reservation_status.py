from typing import Optional

from ..models.factory import Factory


class MedicalInstitutionLocationReservationStatus:
    """旭川市新型コロナワクチン接種医療機関に位置情報をつけたデータを表すモデルオブジェクト

    Attributes:
        name (str): 医療機関の名称
        address (str): 医療機関の住所
        phone_number (str): 医療機関の電話番号
        book_at_medical_institution (bool): 医療機関で予約が可能か
        book_at_call_center (bool): コールセンターやインターネットで予約が可能か
        area (str): 医療機関の地区
        memo (str): 備考
        target_age (str): 対象年齢が16歳以上または12歳から15歳までのいずれか
        latitude (float): 医療機関のある緯度
        longitude (float): 医療機関のある経度
        status (str): 予約受付状況または受付開始時期
        target_person (str): 対象者
        inoculation_time (str): 接種期間・時期
        reservation_status_memo (str): 予約受付状況の備考

    """

    def __init__(
        self,
        name: str,
        address: str,
        phone_number: str,
        book_at_medical_institution: bool,
        book_at_call_center: bool,
        area: str,
        memo: str,
        target_age: str,
        latitude: float,
        longitude: float,
        status: Optional[str],
        target_person: Optional[str],
        inoculation_time: Optional[str],
        reservation_status_memo: Optional[str],
    ):
        """
        Args:
            name (str): 医療機関の名称
            address (str): 医療機関の住所
            phone_number (str): 医療機関の電話番号
            book_at_medical_institution (bool): 医療機関で予約が可能か
            book_at_call_center (bool): コールセンターやインターネットで予約が可能か
            area (str): 医療機関の地区
            memo (str): 備考
            target_age (str): 対象年齢が16歳以上または12歳から15歳までのいずれか
            latitude (float): 医療機関のある緯度
            longitude (float): 医療機関のある経度
            status (str): 予約受付状況または受付開始時期
            target_person (str): 対象者
            inoculation_time (str): 接種期間・時期
            reservation_status_memo (str): 予約受付状況の備考

        """
        self.__name = name
        self.__address = address
        self.__phone_number = phone_number
        self.__book_at_medical_institution = book_at_medical_institution
        self.__book_at_call_center = book_at_call_center
        self.__area = area
        self.__memo = memo
        self.__target_age = target_age
        self.__latitude = latitude
        self.__longitude = longitude
        if status is None:
            self.__status = ""
        else:
            self.__status = status
        if target_person is None:
            self.__target_person = ""
        else:
            self.__target_person = target_person
        if inoculation_time is None:
            self.__inoculation_time = ""
        else:
            self.__inoculation_time = inoculation_time
        if reservation_status_memo is None:
            self.__reservation_status_memo = ""
        else:
            self.__reservation_status_memo = reservation_status_memo

    @property
    def name(self):
        return self.__name

    @property
    def address(self):
        return self.__address

    @property
    def phone_number(self):
        return self.__phone_number

    @property
    def book_at_medical_institution(self):
        return self.__book_at_medical_institution

    @property
    def book_at_call_center(self):
        return self.__book_at_call_center

    @property
    def area(self):
        return self.__area

    @property
    def memo(self):
        return self.__memo

    @property
    def target_age(self):
        return self.__target_age

    @property
    def longitude(self):
        return self.__longitude

    @property
    def latitude(self):
        return self.__latitude

    @property
    def status(self):
        return self.__status

    @property
    def target_person(self):
        return self.__target_person

    @property
    def inoculation_time(self):
        return self.__inoculation_time

    @property
    def reservation_status_memo(self):
        return self.__reservation_status_memo


class MedicalInstitutionLocationReservationStatusFactory(Factory):
    """旭川市新型コロナワクチン接種医療機関を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`MedicalInstitutionLocationReservationStatus`): 医療機関一覧リスト
            MedicalInstitutionLocationReservationStatusクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> MedicalInstitutionLocationReservationStatus:
        """MedicalInstitutionLocationReservationStatusオブジェクトの生成

        Args:
            row (dict): 医療機関データの辞書
                新型コロナワクチン接種医療機関データオブジェクトを作成するための引数

        Returns:
            item (:obj:`MedicalInstitutionLocationReservationStatus`): 医療機関データ
                MedicalInstitutionLocationReservationStatusクラスのオブジェクト

        """
        return MedicalInstitutionLocationReservationStatus(**row)

    def _register_item(self, item: MedicalInstitutionLocationReservationStatus):
        """MedicalInstitutionLocationReservationStatusオブジェクトをリストへ追加

        Args:
            item (:obj:`MedicalInstitutionLocationReservationStatus`): データオブジェクト
                MedicalInstitutionLocationReservationStatusクラスのオブジェクト

        """
        self.__items.append(item)
