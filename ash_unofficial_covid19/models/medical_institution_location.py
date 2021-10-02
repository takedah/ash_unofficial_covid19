from ..models.factory import Factory


class MedicalInstitutionLocation:
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


class MedicalInstitutionLocationFactory(Factory):
    """旭川市新型コロナワクチン接種医療機関を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`MedicalInstitutionLocation`): 医療機関一覧リスト
            MedicalInstitutionLocationクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> MedicalInstitutionLocation:
        """MedicalInstitutionLocationオブジェクトの生成

        Args:
            row (dict): 医療機関データの辞書
                新型コロナワクチン接種医療機関データオブジェクトを作成するための引数

        Returns:
            item (:obj:`MedicalInstitutionLocation`): 医療機関データ
                MedicalInstitutionLocationクラスのオブジェクト

        """
        return MedicalInstitutionLocation(**row)

    def _register_item(self, item: MedicalInstitutionLocation):
        """MedicalInstitutionLocationオブジェクトをリストへ追加

        Args:
            item (:obj:`MedicalInstitutionLocation`): データオブジェクト
                MedicalInstitutionLocationクラスのオブジェクト

        """
        self.__items.append(item)
