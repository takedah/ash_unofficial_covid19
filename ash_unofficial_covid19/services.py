from datetime import date, datetime, timedelta, timezone
from typing import Optional

import psycopg2
from psycopg2.extras import DictCursor

from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.errors import DatabaseConnectionError, ServiceError
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.models import (
    AsahikawaPatientFactory,
    HokkaidoPatientFactory,
    MedicalInstitutionFactory
)


class Service:
    """新型コロナウイルス関連データを扱うサービスクラス"""

    def __init__(self, table_name: str):
        """
        Args:
            table_name (str): テーブル名

        """
        self.__table_name = table_name
        self.__dsn = Config.DATABASE_URL
        self.__logger = AppLog()

    @property
    def table_name(self):
        return self.__table_name

    def get_connection(self):
        """データベース接続オブジェクトを返す

        Returns:
            conn (:obj:`psycopg2.connection`): psycopg2.connectionオブジェクト

        """
        try:
            conn = psycopg2.connect(self.__dsn)
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            self.error_log("データベースに接続できませんでした。")
            raise DatabaseConnectionError(e.args[0])
        return conn

    def delete_all(self) -> None:
        """テーブルのデータを全削除する。"""
        state = "TRUNCATE TABLE " + self.table_name + " RESTART IDENTITY;"
        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(state)
                conn.commit()
                self.info_log(self.table_name + "テーブルを初期化しました。")
            except (
                psycopg2.DataError,
                psycopg2.IntegrityError,
                psycopg2.InternalError,
            ) as e:
                self.error_log(self.table_name + "テーブルを初期化できませんでした。")
                raise ServiceError(e.args[0])

    def upsert(self, items: tuple, primary_key: str, data_lists: list) -> None:
        """データベースのテーブルへデータをバルクインサートでUPSERT登録する。

        Args:
            items (tuple): カラム名のタプル
            primary_key (str): UPSERTを判断するキー名
            data_lists (list of list): 登録データの二次元配列リスト

        """
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
            + self.table_name
            + " "
            + "("
            + column_names[1:]
            + ")"
            + " "
            + "VALUES ("
            + place_holders[1:]
            + ")"
            + " "
            + "ON CONFLICT("
            + primary_key
            + ")"
            + " "
            + "DO UPDATE SET"
            + " "
            + upsert[1:]
        )

        insert_lists = list()
        for data in data_lists:
            # UPSERT句用にリストを重複させる。
            values = tuple(data + data)
            insert_lists.append(values)

        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.executemany(state, insert_lists)
                conn.commit()
            except (
                psycopg2.DataError,
                psycopg2.IntegrityError,
                psycopg2.InternalError,
            ) as e:
                self.error_log(self.table_name + "テーブルへデータを登録できませんでした。")
                raise ServiceError(e.args[0])

    def get_last_updated(self) -> Optional[datetime]:
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (:obj:`datetime.datetime'): 対象テーブルのupdatedカラムで一番最新の値を返す。

        """
        state = "SELECT max(updated_at) FROM " + self.table_name + ";"
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                result = cur.fetchone()
        if result["max"] is None:
            return None
        else:
            return result["max"]

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


class AsahikawaPatientService(Service):
    """旭川市の公表する新型コロナウイルス感染症患者データを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "asahikawa_patients")

    def create(self, patients: AsahikawaPatientFactory) -> None:
        """データベースへ新型コロナウイルス感染症患者データを一括登録する

        Args:
            patients (:obj:`AsahikawaPatientFactory`): 患者データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
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
        )
        # バルクインサートするデータのリストを作成
        data_lists = list()
        for patient in patients.items:
            data_lists.append(
                [
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
            )
            self.upsert(
                items=items,
                primary_key="patient_number",
                data_lists=data_lists,
            )

    def delete(self, patient_number: int) -> bool:
        """指定した識別番号の陽性患者データを削除する

        Args:
            patient_number (int): 削除する陽性患者データの識別番号

        Returns:
            bool: データ削除に成功したら真を返す

        """
        state = "DELETE from asahikawa_patients WHERE patient_number = %s;"
        values = (patient_number,)
        result = False
        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(state, values)
                    if cur.statusmessage == "DELETE 1":
                        result = True
                conn.commit()
            except (
                psycopg2.DataError,
                psycopg2.IntegrityError,
                psycopg2.InternalError,
            ) as e:
                self.error_log(e.args[0])
        return result

    def find_all(self) -> AsahikawaPatientFactory:
        """新型コロナウイルス感染症患者の全件を返す

        Returns:
            res (:obj:`AsahikawaPatientFactory`): 新型コロナウイルス感染症患者オブジェクトの全件リストを要素に持つリスト

        """
        state = (
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
            + self.table_name
            + " "
            + "AS a"
            + " "
            + "LEFT JOIN hokkaido_patients AS h"
            + " "
            + "ON a.hokkaido_patient_number = h.patient_number"
            + " "
            + "ORDER BY a.patient_number ASC;"
        )
        factory = AsahikawaPatientFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory

    def get_duplicate_patient_numbers(self) -> list:
        """
        旭川市の公表した陽性患者情報の中に重複があるが、旭川市公式ホームページは重複分も表示されたままなので、
        北海道の公表するオープンデータで重複削除とされているデータに該当する識別番号をリストで返す。

        Returns:
            res (list): 重複削除とされているデータの識別番号

        """
        state = (
            "SELECT"
            + " "
            + "a.patient_number"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "AS a"
            + " "
            + "LEFT JOIN hokkaido_patients AS h"
            + " "
            + "ON a.hokkaido_patient_number = h.patient_number"
            + " "
            + "WHERE h.residence = '重複削除'"
            + " "
            + "ORDER BY a.patient_number ASC;"
        )
        duplicate_patient_numbers = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    duplicate_patient_numbers.append(row["patient_number"])
        return duplicate_patient_numbers

    def get_csv_rows(self) -> list:
        """陽性患者属性CSVファイルを出力するためのリストを返す

        Returns:
            patients_rows (list of list): 陽性患者属性CSVファイルの元となる二次元配列

        """
        patients = self.find_all()
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
        for patient in patients.items:
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
            aggregate_by_weeks (list of tuple): 1週間ごとの日付とその週の新規陽性患者数を要素とするタプル

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
        aggregate_by_weeks = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    aggregate_by_weeks.append((row[0], row[1]))
        return aggregate_by_weeks

    def get_total_by_months(self, from_date: date, to_date: date) -> list:
        """指定した期間の1か月ごとの陽性患者数の累計結果を返す

        Args:
            from_date (obj:`date`): 累計の始期
            to_date (obj:`date`): 累計の終期

        Returns:
            total_by_months (list of tuple): 1か月ごとの年月とその週までの累計陽性患者数を要素とするタプル

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
        total_by_months = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    total_by_months.append((row[0], row[1]))
        return total_by_months


class HokkaidoPatientService(Service):
    """北海道の公表する新型コロナウイルス感染症患者データを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "hokkaido_patients")

    def create(self, patients: HokkaidoPatientFactory) -> None:
        """データベースへ新型コロナウイルス感染症患者データを保存

        Args:
            patient (:obj:`HokkaidoPatientFactory`): 患者データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
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
        )

        data_lists = list()
        for patient in patients.items:
            data_lists.append(
                [
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
            )
        self.upsert(
            items=items,
            primary_key="patient_number",
            data_lists=data_lists,
        )


class MedicalInstitutionService(Service):
    """旭川市新型コロナ接種医療機関データを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "medical_institutions")

    def create(self, medical_institutions: MedicalInstitutionFactory) -> None:
        """データベースへ新型コロナワクチン接種医療機関データを保存

        Args:
            medical_institutions (:obj:`MedicalInstitutionFactory`):
                医療機関データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
            "name",
            "address",
            "phone_number",
            "book_at_medical_institution",
            "book_at_call_center",
            "area",
            "updated_at",
        )

        data_lists = list()
        for medical_institution in medical_institutions.items:
            data_lists.append(
                [
                    medical_institution.name,
                    medical_institution.address,
                    medical_institution.phone_number,
                    medical_institution.book_at_medical_institution,
                    medical_institution.book_at_call_center,
                    medical_institution.area,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )
        self.upsert(
            items=items,
            primary_key="name",
            data_lists=data_lists,
        )

    def find_all(self) -> MedicalInstitutionFactory:
        """新型コロナワクチン接種医療機関の全件リストを返す

        Returns:
            res (:obj:`MedicalInstitutionFactory`): 新型コロナウイルス感染症患者オブジェクトのリストを要素に持つオブジェクト

        """
        state = (
            "SELECT"
            + " "
            + "name,address,phone_number,book_at_medical_institution,"
            + "book_at_call_center,area"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY id"
            + ";"
        )
        factory = MedicalInstitutionFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory

    def get_csv_rows(self) -> list:
        """新型コロナワクチン接種医療機関一覧CSVファイルを出力するためのリストを返す

        Returns:
            rows (list of list): CSVファイルの元となる二次元配列

        """
        medical_institutions = self.find_all()
        rows = list()
        rows.append(
            [
                "地区",
                "医療機関名",
                "住所",
                "電話",
                "かかりつけの医療機関で予約ができます",
                "コールセンターやインターネットで予約ができます",
            ]
        )
        for medical_institution in medical_institutions.items:
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
                        medical_institution.area,
                        medical_institution.name,
                        medical_institution.address,
                        medical_institution.phone_number,
                        book_at_medical_institution,
                        book_at_call_center,
                    ]
                ]
            )
        return rows
