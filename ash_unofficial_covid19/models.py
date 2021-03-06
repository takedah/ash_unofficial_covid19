from datetime import date
from typing import Optional

from ash_unofficial_covid19.errors import DataModelError
from ash_unofficial_covid19.factory import Factory


class Patient:
    """新型コロナウイルス感染症患者を表すデータ

    Attributes:
        patient_number (int): 識別番号
        city_code (str): 総務省の全国地方公共団体コード
        prefecture (str): 都道府県名
        city_name (str): 市区町村名
        publication_date (datetime.date): 情報を公表した年月日
        onset_date (datetime.date): 発症が確認された年月日
        residence (str): 患者の居住地
        age (str): 患者の年代
        sex (str): 患者の性別
        occupation (str): 患者の職業
        status (str): 患者の状態
        symptom (str): 患者の症状
        overseas_travel_history (bool): 患者の海外渡航歴の有無
        be_discharged (bool): 患者退院済みフラグ
        note (str): 備考

    """

    def __init__(
        self,
        patient_number,
        city_code,
        prefecture,
        city_name,
        publication_date,
        onset_date,
        residence,
        age,
        sex,
        occupation,
        status,
        symptom,
        overseas_travel_history,
        be_discharged,
        note,
    ):
        """
        Args:
            patient_number (str): 識別番号
            city_code (str): 総務省の全国地方公共団体コード
            prefecture (str): 都道府県名
            city_name (str): 市区町村名
            publication_date (datetime.date): 情報を公表した年月日
            onset_date (datetime.date): 発症が確認された年月日
            residence (str): 患者の居住地
            age (str): 患者の年代
            sex (str): 患者の性別
            occupation (str): 患者の職業
            status (str): 患者の状態
            symptom (str): 患者の症状
            overseas_travel_history (bool): 患者の海外渡航歴の有無
            be_discharged (bool): 患者退院済みフラグ
            note (str): 備考

        """
        try:
            self.__patient_number = int(patient_number)
        except ValueError as e:
            raise DataModelError("識別番号が正しくありません。: " + e.args[0])

        self.__city_code = city_code
        self.__prefecture = prefecture
        self.__city_name = city_name

        if isinstance(publication_date, date) or publication_date is None:
            self.__publication_date = publication_date
        else:
            raise DataModelError("情報公開日が正しくありません。")

        if isinstance(onset_date, date) or onset_date is None:
            self.__onset_date = onset_date
        else:
            raise DataModelError("発症確認日が正しくありません。")

        self.__residence = residence
        self.__age = age
        self.__sex = sex
        self.__occupation = occupation
        self.__status = status
        self.__symptom = symptom

        if isinstance(overseas_travel_history, bool) or overseas_travel_history is None:
            self.__overseas_travel_history = overseas_travel_history
        else:
            raise DataModelError("海外渡航歴の有無が正しくありません。")

        if isinstance(be_discharged, bool) or be_discharged is None:
            self.__be_discharged = be_discharged
        else:
            raise DataModelError("退院済みフラグが正しくありません。")

        self.__note = note

    @property
    def patient_number(self) -> int:
        return self.__patient_number

    @property
    def city_code(self) -> str:
        return self.__city_code

    @property
    def prefecture(self) -> str:
        return self.__prefecture

    @property
    def city_name(self) -> str:
        return self.__city_name

    @property
    def publication_date(self) -> Optional[date]:
        return self.__publication_date

    @property
    def onset_date(self) -> Optional[date]:
        return self.__onset_date

    @property
    def residence(self) -> str:
        return self.__residence

    @property
    def age(self) -> str:
        return self.__age

    @property
    def sex(self) -> str:
        return self.__sex

    @property
    def occupation(self) -> str:
        return self.__occupation

    @property
    def status(self) -> str:
        return self.__status

    @property
    def symptom(self) -> str:
        return self.__symptom

    @property
    def overseas_travel_history(self) -> Optional[bool]:
        return self.__overseas_travel_history

    @property
    def be_discharged(self) -> Optional[bool]:
        return self.__be_discharged

    @property
    def note(self) -> str:
        return self.__note


class PatientFactory(Factory):
    """新型コロナウイルス感染症患者モデルオブジェクトを生成

    Attributes:
        items (list of :obj:`Patient`): Patientクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, **row) -> Patient:
        """Patientオブジェクトの生成

        Args:
            row (dict): 新型コロナウイルス感染症患者データオブジェクトを作成するための引数

        Returns:
            patient (:obj:`Patient`): Patientクラスのオブジェクト

        """
        return Patient(**row)

    def _register_item(self, item: Patient):
        """Patientオブジェクトをリストへ追加

        Args:
            item (:obj:`Patient`): Patientクラスのオブジェクト

        """
        self.__items.append(item)
