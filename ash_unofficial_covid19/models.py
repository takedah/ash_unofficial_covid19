from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Optional

from ash_unofficial_covid19.errors import DataModelError


class Factory(metaclass=ABCMeta):
    def create(self, **row):
        item = self._create_item(**row)
        self._register_item(item)
        return item

    @abstractmethod
    def _create_item(self, **row):
        pass

    @abstractmethod
    def _register_item(self, item):
        pass


class Patient:
    """新型コロナウイルス感染症患者を表すデータモデルの基底クラス

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
        patient_number: int,
        city_code: str,
        prefecture: str,
        city_name: str,
        publication_date: date,
        onset_date: date,
        residence: str,
        age: str,
        sex: str,
        occupation: str,
        status: str,
        symptom: str,
        overseas_travel_history: bool,
        be_discharged: bool,
        note: str,
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


class AsahikawaPatient(Patient):
    """旭川市の公表する新型コロナウイルス感染症患者を表すデータ

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
        hokkaido_patient_number (int): 北海道発表番号
        surrounding_status (str): 周囲の状況
        close_contact (str): 濃厚接触者の状況

    """

    def __init__(
        self,
        patient_number: int,
        city_code: str,
        prefecture: str,
        city_name: str,
        publication_date: date,
        onset_date: date,
        residence: str,
        age: str,
        sex: str,
        occupation: str,
        status: str,
        symptom: str,
        overseas_travel_history: bool,
        be_discharged: bool,
        note: str,
        hokkaido_patient_number: int,
        surrounding_status: str,
        close_contact: str,
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
            hokkaido_patient_number (int): 北海道発表番号
            surrounding_status (str): 周囲の状況
            close_contact (str): 濃厚接触者の状況

        """
        Patient.__init__(
            self,
            patient_number=patient_number,
            city_code=city_code,
            prefecture=prefecture,
            city_name=city_name,
            publication_date=publication_date,
            onset_date=onset_date,
            residence=residence,
            age=age,
            sex=sex,
            occupation=occupation,
            status=status,
            symptom=symptom,
            overseas_travel_history=overseas_travel_history,
            be_discharged=be_discharged,
            note=note,
        )
        try:
            self.__hokkaido_patient_number = int(hokkaido_patient_number)
        except ValueError as e:
            raise DataModelError("北海道発表番号が正しくありません。: " + e.args[0])

        self.__surrounding_status = surrounding_status
        self.__close_contact = close_contact

    @property
    def hokkaido_patient_number(self) -> int:
        return self.__hokkaido_patient_number

    @property
    def surrounding_status(self) -> str:
        return self.__surrounding_status

    @property
    def close_contact(self) -> str:
        return self.__close_contact


class AsahikawaPatientFactory(Factory):
    """旭川市の公表する新型コロナウイルス感染症患者モデルオブジェクトを生成

    Attributes:
        items (list of :obj:`AsahikawaPatient`): 旭川市の患者データリスト
            AsahikawaPatientクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, **row) -> AsahikawaPatient:
        """AsahikawaPatientオブジェクトの生成

        Args:
            row (dict): 旭川市の患者データの辞書
                新型コロナウイルス感染症患者データオブジェクトを作成するための引数

        Returns:
            patient (:obj:`AsahikawaPatient`): AsahikawaPatientクラスのオブジェクト

        """
        return AsahikawaPatient(**row)

    def _register_item(self, item: AsahikawaPatient):
        """AsahikawaPatientオブジェクトをリストへ追加

        Args:
            item (:obj:`AsahikawaPatient`): AsahikawaPatientクラスのオブジェクト

        """
        self.__items.append(item)


class HokkaidoPatient(Patient):
    """北海道で公表している新型コロナウイルス感染症患者を表すデータ

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
        patient_number: int,
        city_code: str,
        prefecture: str,
        city_name: str,
        publication_date: date,
        onset_date: date,
        residence: str,
        age: str,
        sex: str,
        occupation: str,
        status: str,
        symptom: str,
        overseas_travel_history: bool,
        be_discharged: bool,
        note: str,
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
        Patient.__init__(
            self,
            patient_number=patient_number,
            city_code=city_code,
            prefecture=prefecture,
            city_name=city_name,
            publication_date=publication_date,
            onset_date=onset_date,
            residence=residence,
            age=age,
            sex=sex,
            occupation=occupation,
            status=status,
            symptom=symptom,
            overseas_travel_history=overseas_travel_history,
            be_discharged=be_discharged,
            note=note,
        )


class HokkaidoPatientFactory(Factory):
    """北海道の公表する新型コロナウイルス感染症患者モデルオブジェクトを生成

    Attributes:
        items (list of :obj:`HokkaidoPatient`): 北海道の患者データリスト
            HokkaidoPatientクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, **row) -> HokkaidoPatient:
        """HokkaidoPatientオブジェクトの生成

        Args:
            row (dict): 北海道の患者データの辞書
                新型コロナウイルス感染症患者データオブジェクトを作成するための引数

        Returns:
            patient (:obj:`HokkaidoPatient`): HokkaidoPatientクラスのオブジェクト

        """
        return HokkaidoPatient(**row)

    def _register_item(self, item: Patient):
        """Patientオブジェクトをリストへ追加

        Args:
            item (:obj:`HokkaidoPatient`): HokkaidoPatientクラスのオブジェクト

        """
        self.__items.append(item)


class MedicalInstitution:
    """旭川市新型コロナワクチン接種医療機関を表すモデルオブジェクト

    Attributes:
        name (str): 医療機関の名称
        address (str): 医療機関の住所
        phone_number (str): 医療機関の電話番号
        book_at_medical_institution (bool): 医療機関で予約が可能か
        book_at_call_center (bool): コールセンターやインターネットで予約が可能か
        area (str): 医療機関の地区

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

        """
        self.__name = name
        self.__address = address
        self.__phone_number = phone_number
        self.__book_at_medical_institution = book_at_medical_institution
        self.__book_at_call_center = book_at_call_center
        self.__area = area
        self.__memo = memo

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

    def _register_item(self, item: Patient):
        """MedicalInstitutionオブジェクトをリストへ追加

        Args:
            item (:obj:`MedicalInstitution`): MedicalInstitutionクラスのオブジェクト

        """
        self.__items.append(item)
