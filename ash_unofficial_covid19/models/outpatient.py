import urllib.parse
from dataclasses import dataclass, field
from typing import Optional

from ..models.factory import Factory


@dataclass()
class Outpatient:
    """新型コロナ発熱外来を表すモデルオブジェクト

    Attributes:
        is_outpatient (bool): 外来対応医療機関か
        is_positive_patients (bool): 陽性者（療養者）の治療に関与する医療機関か
        public_health_care_center (str): 保健所
        medical_institution_name (str): 医療機関名
        city (str): 市町村
        address (str): 住所
        phone_number (str): 電話番号（予約URL）
        is_target_not_family (bool): かかりつけ患者以外の診療の可否
        is_pediatrics (str): 小児対応の可否
        mon (str): 月曜日の診療時間
        tue (str): 火曜日の診療時間
        wed (str): 水曜日の診療時間
        thu (str): 木曜日の診療時間
        fri (str): 金曜日の診療時間
        sat (str): 土曜日の診療時間
        sun (str): 日曜日の診療時間
        is_face_to_face_for_positive_patients (bool): 陽性者（療養者）への外来対応（対面）
        is_online_for_positive_patients (bool): 陽性者（療養者）へのオンライン診療対応（電話診療を含む）
        is_home_visitation_for_positive_patients (bool): 陽性者（療養者）への訪問診療
        memo (str): 備考

    """

    is_outpatient: Optional[bool]
    is_positive_patients: Optional[bool]
    public_health_care_center: str
    medical_institution_name: str
    city: str
    address: str
    phone_number: str
    is_target_not_family: Optional[bool]
    is_pediatrics: Optional[bool]
    mon: str
    tue: str
    wed: str
    thu: str
    fri: str
    sat: str
    sun: str
    is_face_to_face_for_positive_patients: Optional[bool]
    is_online_for_positive_patients: Optional[bool]
    is_home_visitation_for_positive_patients: Optional[bool]
    memo: str = ""


class OutpatientFactory(Factory):
    """新型コロナ発熱外来を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`Outpatient`): 発熱外来一覧リスト
            Outpatientクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> Outpatient:
        """Outpatientオブジェクトの生成

        Args:
            row (dict): 発熱外来データの辞書
                新型コロナ発熱外来データオブジェクトを
                作成するための引数

        Returns:
            reservation_status (:obj:`Outpatient`): 発熱外来データ
                Outpatientクラスのオブジェクト

        """
        return Outpatient(**row)

    def _register_item(self, item: Outpatient):
        """Outpatientオブジェクトをリストへ追加

        Args:
            item (:obj:`Outpatient`): Outpatientクラスのオブジェクト

        """
        self.__items.append(item)


@dataclass()
class OutpatientLocation(Outpatient):
    """新型コロナ発熱外来詳細データモデル

    新型コロナ発熱外来に位置情報を加えたデータモデル。

    Attributes:
        is_outpatient (bool): 外来対応医療機関か
        is_positive_patients (bool): 陽性者（療養者）の治療に関与する医療機関か
        public_health_care_center (str): 保健所
        medical_institution_name (str): 医療機関名
        city (str): 市町村
        address (str): 住所
        phone_number (str): 電話番号（予約URL）
        is_target_not_family (bool): かかりつけ患者以外の診療の可否
        is_pediatrics (str): 小児対応の可否
        mon (str): 月曜日の診療時間
        tue (str): 火曜日の診療時間
        wed (str): 水曜日の診療時間
        thu (str): 木曜日の診療時間
        fri (str): 金曜日の診療時間
        sat (str): 土曜日の診療時間
        sun (str): 日曜日の診療時間
        is_face_to_face_for_positive_patients (bool): 陽性者（療養者）への外来対応（対面）
        is_online_for_positive_patients (bool): 陽性者（療養者）へのオンライン診療対応（電話診療を含む）
        is_home_visitation_for_positive_patients (bool): 陽性者（療養者）への訪問診療
        memo (str): 備考
        medical_institution_name_url (str): 医療機関の名称をURLパースした文字列

    """

    latitude: float = 0
    longitude: float = 0
    medical_institution_name_url: str = field(init=False)

    def __post_init__(self):
        self.medical_institution_name_url = urllib.parse.quote(self.medical_institution_name)


class OutpatientLocationFactory(Factory):
    """新型コロナ発熱外来詳細オブジェクトを生成

    Attributes:
        items (list of :obj:`OutpatientLocation`): 発熱外来詳細リスト
            OutpatientLocationクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> OutpatientLocation:
        """OutpatientLocationオブジェクトの生成

        Args:
            row (dict): 発熱外来詳細データの辞書
                新型コロナ発熱外来詳細データオブジェクトを
                作成するための引数

        Returns:
            item (:obj:`OutpatientLocation`): 発熱外来詳細データ
                OutpatientLocationクラスのオブジェクト

        """
        return OutpatientLocation(**row)

    def _register_item(self, item: OutpatientLocation):
        """OutpatientLocationオブジェクトをリストへ追加

        Args:
            item (:obj:`OutpatientLocation`): データオブジェクト
                OutpatientLocationクラスのオブジェクト

        """
        self.__items.append(item)
