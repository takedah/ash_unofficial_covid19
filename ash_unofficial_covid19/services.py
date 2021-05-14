from datetime import date, datetime, timedelta, timezone
from typing import Optional

import psycopg2
from psycopg2.extras import DictCursor

from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.errors import DatabaseError, DataError
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.models import (
    AsahikawaPatient,
    AsahikawaPatientFactory,
    HokkaidoPatient,
    MedicalInstitution,
    MedicalInstitutionFactory
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

    def statusmessage(self) -> str:
        """クエリ実行後のメッセージを返す

        Returns:
            status_message (str): クエリ実行後メッセージ

        """
        return self.__cursor.statusmessage

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

    def delete(self, patient_number: int) -> bool:
        """指定した識別番号の陽性患者データを削除する

        Args:
            patient_number (int): 削除する陽性患者データの識別番号

        Returns:
            bool: データ削除に成功したら真を返す

        """
        state = "DELETE from asahikawa_patients WHERE patient_number = %s;"
        values = (patient_number,)
        try:
            self.execute(state, values)
            result = self.statusmessage()
            if result == "DELETE 1":
                return True
            else:
                return False
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
            + "a.patient_number,a.city_code,a.prefecture,a.city_name,"
            + "a.publication_date,"
            + "h.onset_date,a.residence,a.age,a.sex,h.occupation,h.status,h.symptom,"
            + "h.overseas_travel_history,h.be_discharged,a.note,"
            + "a.hokkaido_patient_number,a.surrounding_status,a.close_contact"
            + " "
            + "FROM"
            + " "
            + self.__table_name
            + " "
            + "AS a"
            + " "
            + "LEFT JOIN hokkaido_patients AS h"
            + " "
            + "ON a.hokkaido_patient_number = h.patient_number"
            + " "
            + "ORDER BY a.patient_number ASC;",
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

    def get_duplicate_patient_numbers(self) -> list:
        """
        旭川市の公表した陽性患者情報の中に重複があるが、旭川市公式ホームページは
        重複分も表示されたままなので、北海道の公表するオープンデータで重複削除と
        されているデータに該当する識別番号をリストで返す。

        Returns:
            res (list): 重複削除とされているデータの識別番号

        """
        self.execute(
            "SELECT"
            + " "
            + "a.patient_number"
            + " "
            + "FROM"
            + " "
            + self.__table_name
            + " "
            + "AS a"
            + " "
            + "LEFT JOIN hokkaido_patients AS h"
            + " "
            + "ON a.hokkaido_patient_number = h.patient_number"
            + " "
            + "WHERE h.residence = '重複削除'"
            + " "
            + "ORDER BY a.patient_number ASC;",
        )
        duplicate_patient_numbers = list()
        for row in self.fetchall():
            duplicate_patient_numbers.append(row["patient_number"])
        return duplicate_patient_numbers

    def get_patients_csv_rows(self) -> list:
        """陽性患者属性CSVファイルを出力するためのリストを返す

        Returns:
            patients_rows (list of list): 陽性患者属性CSVファイルの元となる二次元配列

        """
        patients = self.find()
        rows = list()
        rows.append(
            [
                "No",
                "全国地方公共団体コード",
                "都道府県名",
                "市区町村名",
                "公表_年月日",
                "発症_年月日",
                "患者_居住地",
                "患者_年代",
                "患者_性別",
                "患者_職業",
                "患者_状態",
                "患者_症状",
                "患者_渡航歴の有無フラグ",
                "患者_退院済フラグ",
                "備考",
            ]
        )
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
                    "" if v is None else v
                    for v in [
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
                ]
            )
        return rows

    def get_aggregate_by_weeks(self, from_date: date, to_date: date) -> list:
        """指定した期間の1週間ごとの陽性患者数の集計結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            aggregate_by_weeks (list of tuple): 1週間ごとの日付とその週の
                新規陽性患者数を要素とするタプル

        """
        state = (
            "SELECT to_char(to_week, 'MM-DD') AS weeks, "
            + "COUNT(DISTINCT patient_number) AS patients FROM "
            + "(SELECT generate_series AS from_week, "
            + "generate_series + '7 days'::interval AS to_week FROM "
            + "generate_series('"
            + from_date.strftime("%Y-%m-%d")
            + "'::DATE, '"
            + to_date.strftime("%Y-%m-%d")
            + "'::DATE, '7 days')) "
            + "AS week_ranges LEFT JOIN asahikawa_patients ON "
            + "from_week <= asahikawa_patients.publication_date AND "
            + "asahikawa_patients.publication_date < to_week GROUP BY to_week;"
        )
        self.execute(state)
        aggregate_by_weeks = list()
        for row in self.fetchall():
            aggregate_by_weeks.append((row[0], row[1]))

        return aggregate_by_weeks

    def get_total_by_months(self, from_date: date, to_date: date) -> list:
        """指定した期間の1か月ごとの陽性患者数の累計結果を返す

        Args:
            from_date (obj:`date`): 累計の始期
            to_date (obj:`date`): 累計の終期

        Returns:
            total_by_months (list of tuple): 1か月ごとの年月とその週までの
                累計陽性患者数を要素とするタプル

        """
        state = (
            "SELECT to_char(aggregate_patients.from_month, 'YYYY-MM'), "
            + "SUM(aggregate_patients.patients) OVER("
            + "ORDER BY aggregate_patients.from_month) AS total_patients FROM "
            + "("
            + "SELECT from_month, COUNT(DISTINCT patient_number) as patients FROM "
            + "("
            + "SELECT generate_series AS from_month, generate_series + "
            + "'1 months'::interval AS to_month FROM generate_series('"
            + from_date.strftime("%Y-%m-%d")
            + "'::DATE, '"
            + to_date.strftime("%Y-%m-%d")
            + "'::DATE, '1 months')"
            + ") AS month_ranges "
            + "LEFT JOIN asahikawa_patients "
            + "ON from_month <= asahikawa_patients.publication_date AND "
            + "asahikawa_patients.publication_date < to_month GROUP BY from_month"
            + ") AS aggregate_patients;"
        )
        self.execute(state)
        total_by_months = list()
        for row in self.fetchall():
            total_by_months.append((row[0], row[1]))

        return total_by_months


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


class MedicalInstitutionService:
    """旭川市新型コロナ接種医療機関データを扱うサービスの基底クラス"""

    def __init__(self, db: DB):
        """
        Args:
            db (:obj:`DB`): データベース操作をラップしたオブジェクト

        """

        self.__table_name = "medical_institutions"
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

    def statusmessage(self) -> str:
        """クエリ実行後のメッセージを返す

        Returns:
            status_message (str): クエリ実行後メッセージ

        """
        return self.__cursor.statusmessage

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

    def truncate(self) -> None:
        """医療機関テーブルのデータを全削除"""

        state = "TRUNCATE TABLE " + self.__table_name + " RESTART IDENTITY;"
        self.execute(state)
        self.info_log(self.__table_name + "テーブルを初期化しました。")

    def create(self, medical_institution: MedicalInstitution) -> bool:
        """データベースへ新型コロナワクチン接種医療機関データを保存

        Args:
            medical_institution (:obj:`MedicalInstitution`): 医療機関データのオブジェクト

        Returns:
            bool: データの登録が成功したらTrueを返す

        """
        items = [
            "name",
            "address",
            "phone_number",
            "book_at_medical_institution",
            "book_at_call_center",
            "area",
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
            + "ON CONFLICT(name)"
            + " "
            + "DO UPDATE SET"
            + " "
            + upsert[1:]
        )

        temp_values = [
            medical_institution.name,
            medical_institution.address,
            medical_institution.phone_number,
            medical_institution.book_at_medical_institution,
            medical_institution.book_at_call_center,
            medical_institution.area,
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
        """新型コロナワクチン接種医療機関オブジェクトのリストを返す

        Returns:
            res (list of :obj:`MedicalInstitution`): 新型コロナウイルス感染症患者オブジェクトのリスト

        """
        self.execute(
            "SELECT"
            + " "
            + "name,address,phone_number,book_at_medical_institution,"
            + "book_at_call_center,area"
            + " "
            + "FROM"
            + " "
            + self.__table_name
            + ";",
        )
        factory = MedicalInstitutionFactory()
        for row in self.fetchall():
            factory.create(**row)
        return factory.items

    def get_last_updated(self) -> Optional[datetime]:
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (:obj:`datetime.datetime'): medical_institutionsテーブルの
                updatedカラムで一番最新の値を返す。

        """
        self.execute("SELECT max(updated_at) FROM " + self.__table_name + ";")
        row = self.fetchone()
        if row["max"] is None:
            return None
        else:
            return row["max"]

    def get_csv_rows(self) -> list:
        """新型コロナワクチン接種医療機関一覧CSVファイルを出力するためのリストを返す

        Returns:
            rows (list of list): CSVファイルの元となる二次元配列

        """
        medical_institutions = self.find()
        rows = list()
        rows.append(
            [
                "医療機関名",
                "住所",
                "電話",
                "かかりつけの医療機関で予約ができます",
                "コールセンターやインターネットで予約ができます",
                "地区",
            ]
        )
        for medical_institution in medical_institutions:
            if medical_institution.book_at_medical_institution is None:
                book_at_medical_institution = ""
            else:
                book_at_medical_institution = str(
                    int(medical_institution.book_at_medical_institution)
                )
            if medical_institution.book_at_call_center is None:
                book_at_call_center = ""
            else:
                book_at_call_center = str(int(medical_institution.book_at_call_center))

            rows.append(
                [
                    "" if v is None else v
                    for v in [
                        medical_institution.name,
                        medical_institution.address,
                        medical_institution.phone_number,
                        book_at_medical_institution,
                        book_at_call_center,
                        medical_institution.area,
                    ]
                ]
            )
        return rows
