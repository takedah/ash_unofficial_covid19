from ash_unofficial_covid19.models.factory import Factory


class MedicalInstitution:
    """旭川市新型コロナワクチン接種医療機関を表すモデルオブジェクト

    Attributes:
        name (str): 医療機関の名称
        address (str): 医療機関の住所
        phone_number (str): 医療機関の電話番号
        book_at_medical_institution (bool): 医療機関で予約が可能か
        book_at_call_center (bool): コールセンターやインターネットで予約が可能か
        area (str): 医療機関の地区
        memo (str): 備考
        target_age (str): 対象年齢が16歳以上または12歳から15歳までのいずれか

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

        """
        self.__name = name
        self.__address = address
        self.__phone_number = phone_number
        self.__book_at_medical_institution = book_at_medical_institution
        self.__book_at_call_center = book_at_call_center
        self.__area = area
        self.__memo = memo
        self.__target_age = target_age

    @property
    def name(self) -> str:
        return self.__name

    @property
    def address(self) -> str:
        return self.__address

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def book_at_medical_institution(self) -> bool:
        return self.__book_at_medical_institution

    @property
    def book_at_call_center(self) -> bool:
        return self.__book_at_call_center

    @property
    def area(self) -> str:
        return self.__area

    @property
    def memo(self) -> str:
        return self.__memo

    @property
    def target_age(self) -> str:
        return self.__target_age


class MedicalInstitutionFactory(Factory):
    """旭川市新型コロナワクチン接種医療機関を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`MedicalInstitution`): 医療機関一覧リスト
            MedicalInstitutionクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, **row) -> MedicalInstitution:
        """MedicalInstitutionオブジェクトの生成

        Args:
            row (dict): 医療機関データの辞書
                新型コロナワクチン接種医療機関データオブジェクトを作成するための引数

        Returns:
            medical_institution (:obj:`MedicalInstitution`): 医療機関データ
                MedicalInstitutionクラスのオブジェクト

        """
        return MedicalInstitution(**row)

    def _register_item(self, item: MedicalInstitution):
        """MedicalInstitutionオブジェクトをリストへ追加

        Args:
            item (:obj:`MedicalInstitution`): MedicalInstitutionクラスのオブジェクト

        """
        self.__items.append(item)
