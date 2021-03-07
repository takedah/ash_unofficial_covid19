from datetime import datetime, timedelta, timezone
from typing import Optional

import psycopg2
from psycopg2.extras import DictCursor

from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.errors import DatabaseError, DataError
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.models import (
    AsahikawaPatient,
    AsahikawaPatientFactory,
    HokkaidoPatient
)


class PatientService:
    """新型コロナウイルス感染症患者データを扱うサービスの基底クラス"""

    def __init__(self, db: DB):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト

        """

        self.__cursor = db.cursor()
        self.__logger = AppLog()

    def execute(self, sql: str, parameters: tuple = None) -> bool:
        """DictCursorオブジェクトのexecuteメソッドのラッパー

        Args:
            sql (str): SQL文
            parameters (tuple): SQLにプレースホルダを使用する場合の値を格納したリスト

        """
        try:
            if parameters:
                self.__cursor.execute(sql, parameters)
            else:
                self.__cursor.execute(sql)
            return True
        except (
            psycopg2.DataError,
            psycopg2.IntegrityError,
            psycopg2.InternalError,
        ) as e:
            raise DataError(e.args[0])

    def fetchone(self) -> DictCursor:
        """DictCursorオブジェクトのfetchoneメソッドのラッパー

        Returns:
            results (:obj:`DictCursor`): 検索結果のイテレータ

        """
        return self.__cursor.fetchone()

    def fetchall(self) -> list:
        """DictCursorオブジェクトのfetchallメソッドのラッパー

        Returns:
            results (list of :obj:`DictCursor`): 検索結果のイテレータのリスト

        """
        return self.__cursor.fetchall()

    def info_log(self, message) -> None:
        """AppLogオブジェクトのinfoメソッドのラッパー。

        Args:
            message (str): 通常のログメッセージ
        """
        self.__logger.info(message)

    def error_log(self, message) -> None:
        """AppLogオブジェクトのerrorメソッドのラッパー。

        Args:
            message (str): エラーログメッセージ

        """
        self.__logger.error(message)


class AsahikawaPatientService(PatientService):
    """旭川市の公表する新型コロナウイルス感染症患者データを扱うサービス"""

    def __init__(self, db: DB):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト

        """

        PatientService.__init__(self, db)
        self.__table_name = "asahikawa_patients"

    def truncate(self) -> None:
        """患者テーブルのデータを全削除"""

        state = "TRUNCATE TABLE " + self.__table_name + " RESTART IDENTITY;"
        self.execute(state)
        self.info_log(self.__table_name + "テーブルを初期化しました。")

    def create(self, patient: AsahikawaPatient) -> bool:
        """データベースへ新型コロナウイルス感染症患者データを保存

        Args:
            patient (:obj:`AsahikawaPatient`): 患者データのオブジェクト

        Returns:
            bool: データの登録が成功したらTrueを返す

        """
        items = [
            "patient_number",
            "city_code",
            "prefecture",
            "city_name",
            "publication_date",
            "onset_date",
            "residence",
            "age",
            "sex",
            "occupation",
            "status",
            "symptom",
            "overseas_travel_history",
            "be_discharged",
            "note",
            "hokkaido_patient_number",
            "surrounding_status",
            "close_contact",
            "updated_at",
        ]

        column_names = ""
        place_holders = ""
        upsert = ""
        for item in items:
            column_names += "," + item
            place_holders += ",%s"
            upsert += "," + item + "=%s"

        state = (
            "INSERT INTO"
            + " "
            + self.__table_name
            + " "
            + "("
            + column_names[1:]
            + ")"
            + " "
            + "VALUES ("
            + place_holders[1:]
            + ")"
            + " "
            + "ON CONFLICT(patient_number)"
            + " "
            + "DO UPDATE SET"
            + " "
            + upsert[1:]
        )

        temp_values = [
            patient.patient_number,
            patient.city_code,
            patient.prefecture,
            patient.city_name,
            patient.publication_date,
            patient.onset_date,
            patient.residence,
            patient.age,
            patient.sex,
            patient.occupation,
            patient.status,
            patient.symptom,
            patient.overseas_travel_history,
            patient.be_discharged,
            patient.note,
            patient.hokkaido_patient_number,
            patient.surrounding_status,
            patient.close_contact,
            datetime.now(timezone(timedelta(hours=+9))),
        ]
        # UPDATE句用にリストを重複させる。
        values = tuple(temp_values + temp_values)

        try:
            self.execute(state, values)
            return True
        except (DatabaseError, DataError) as e:
            self.error_log(e.message)
            return False

    def find(self) -> list:
        """新型コロナウイルス感染症患者オブジェクトのリストを返す

        Returns:
            res (list of :obj:`AsahikawaPatient`): 新型コロナウイルス感染症患者オブジェクトのリスト

        """
        self.execute(
            "SELECT"
            + " "
            + "patient_number,city_code,prefecture,city_name,publication_date,"
            + "onset_date,residence,age,sex,occupation,status,symptom,"
            + "overseas_travel_history,be_discharged,note,"
            + "hokkaido_patient_number,surrounding_status,close_contact"
            + " "
            + "FROM"
            + " "
            + self.__table_name
            + " "
            + "ORDER BY patient_number DESC;",
        )
        factory = AsahikawaPatientFactory()
        for row in self.fetchall():
            factory.create(**row)
        return factory.items

    def get_last_updated(self) -> Optional[datetime]:
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (:obj:`datetime.datetime'): patientテーブルのupdatedカラムで一番最新の値を返す。
        """
        self.execute("SELECT max(updated_at) FROM " + self.__table_name + ";")
        row = self.fetchone()
        if row["max"] is None:
            return None
        else:
            return row["max"]

    def get_patients_rows(self) -> list:
        """陽性患者属性CSVファイルをFlaskのResponseオブジェクトで返す

        Returns:
            patients_rows (list of list): 陽性患者属性CSVファイルのReponseオブジェクト

        """
        patients = self.find()
        rows = list()
        for patient in patients:
            patient_number = str(patient.patient_number)

            if patient.publication_date is None:
                publication_date = ""
            else:
                publication_date = patient.publication_date.strftime("%Y-%m-%d")

            if patient.onset_date is None:
                onset_date = ""
            else:
                onset_date = patient.onset_date.strftime("%Y-%m-%d")

            if patient.overseas_travel_history is None:
                overseas_travel_history = ""
            else:
                overseas_travel_history = str(int(patient.overseas_travel_history))

            if patient.be_discharged is None:
                be_discharged = ""
            else:
                be_discharged = str(int(patient.be_discharged))

            rows.append(
                [
                    patient_number,
                    patient.city_code,
                    patient.prefecture,
                    patient.city_name,
                    publication_date,
                    onset_date,
                    patient.residence,
                    patient.age,
                    patient.sex,
                    patient.occupation,
                    patient.status,
                    patient.symptom,
                    overseas_travel_history,
                    be_discharged,
                    patient.note,
                ]
            )
        return rows


class HokkaidoPatientService(PatientService):
    """北海道の公表する新型コロナウイルス感染症患者データを扱うサービス"""

    def __init__(self, db: DB):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト

        """

        PatientService.__init__(self, db)
        self.__table_name = "hokkaido_patients"

    def truncate(self) -> None:
        """患者テーブルのデータを全削除"""

        state = "TRUNCATE TABLE " + self.__table_name + " RESTART IDENTITY;"
        self.execute(state)
        self.info_log(self.__table_name + "テーブルを初期化しました。")

    def create(self, patient: HokkaidoPatient) -> bool:
        """データベースへ新型コロナウイルス感染症患者データを保存

        Args:
            patient (:obj:`HokkaidoPatient`): 患者データのオブジェクト

        Returns:
            bool: データの登録が成功したらTrueを返す

        """
        items = [
            "patient_number",
            "city_code",
            "prefecture",
            "city_name",
            "publication_date",
            "onset_date",
            "residence",
            "age",
            "sex",
            "occupation",
            "status",
            "symptom",
            "overseas_travel_history",
            "be_discharged",
            "note",
            "updated_at",
        ]

        column_names = ""
        place_holders = ""
        upsert = ""
        for item in items:
            column_names += "," + item
            place_holders += ",%s"
            upsert += "," + item + "=%s"

        state = (
            "INSERT INTO"
            + " "
            + self.__table_name
            + " "
            + "("
            + column_names[1:]
            + ")"
            + " "
            + "VALUES ("
            + place_holders[1:]
            + ")"
            + " "
            + "ON CONFLICT(patient_number)"
            + " "
            + "DO UPDATE SET"
            + " "
            + upsert[1:]
        )

        temp_values = [
            patient.patient_number,
            patient.city_code,
            patient.prefecture,
            patient.city_name,
            patient.publication_date,
            patient.onset_date,
            patient.residence,
            patient.age,
            patient.sex,
            patient.occupation,
            patient.status,
            patient.symptom,
            patient.overseas_travel_history,
            patient.be_discharged,
            patient.note,
            datetime.now(timezone(timedelta(hours=+9))),
        ]
        # UPDATE句用にリストを重複させる。
        values = tuple(temp_values + temp_values)

        try:
            self.execute(state, values)
            return True
        except (DatabaseError, DataError) as e:
            self.error_log(e.message)
            return False
