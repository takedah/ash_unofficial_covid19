from ..models.factory import Factory


class ReservationStatus:
    """旭川市新型コロナワクチン接種医療機関予約受付状況を表すモデルオブジェクト

    Attributes:
        medical_institution_name (str): 医療機関の名称
        address (str): 住所
        phone_number (str): 電話番号
        status (str): 予約受付状況または受付開始時期
        inoculation_time (str): 接種期間・時期
        target_age (str): 対象年齢
        target_family (bool): かかりつけの方が対象か
        target_not_family (bool): かかりつけ以外の方が対象か
        target_suberbs (bool): 市外の方が対象か
        memo (str): 備考

    """

    def __init__(
        self,
        medical_institution_name: str,
        address: str,
        phone_number: str,
        status: str,
        inoculation_time: str,
        target_age: str,
        target_family: bool,
        target_not_family: bool,
        target_suberbs: bool,
        target_other: str,
        memo: str,
    ):
        """
        Args:
            medical_institution_name (str): 医療機関の名称
            address (str): 住所
            phone_number (str): 電話番号
            status (str): 予約受付状況または受付開始時期
            inoculation_time (str): 接種期間・時期
            target_age (str): 対象年齢
            target_family (bool): かかりつけの方が対象か
            target_not_family (bool): かかりつけ以外の方が対象か
            target_suberbs (bool): 市外の方が対象か
            target_other (str): その他
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
    def memo(self):
        return self.__memo


class ReservationStatusFactory(Factory):
    """旭川市新型コロナワクチン接種医療機関の予約受付状況を表すモデルオブジェクトを生成

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
            medical_institution (:obj:`ReservationStatus`): 医療機関予約受付状況データ
                ReservationStatusクラスのオブジェクト

        """
        return ReservationStatus(**row)

    def _register_item(self, item: ReservationStatus):
        """ReservationStatusオブジェクトをリストへ追加

        Args:
            item (:obj:`ReservationStatus`): ReservationStatusクラスのオブジェクト

        """
        self.__items.append(item)
