from datetime import datetime, timedelta, timezone
from typing import Optional

from psycopg2.extras import DictCursor

from ash_unofficial_covid19.models.medical_institution import (
    MedicalInstitutionFactory
)
from ash_unofficial_covid19.services.service import Service


class MedicalInstitutionService(Service):
    """旭川市新型コロナ接種医療機関データを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "medical_institutions")

    def create(self, medical_institutions: MedicalInstitutionFactory) -> None:
        """データベースへ新型コロナワクチン接種医療機関データを保存

        Args:
            medical_institutions (:obj:`MedicalInstitutionFactory`): 医療機関データ
                医療機関データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
            "name",
            "address",
            "phone_number",
            "book_at_medical_institution",
            "book_at_call_center",
            "area",
            "memo",
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
                    medical_institution.memo,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="name",
            data_lists=data_lists,
        )

    def find_all(self) -> MedicalInstitutionFactory:
        """新型コロナワクチン接種医療機関の全件リストを返す

        Returns:
            res (:obj:`MedicalInstitutionFactory`): 医療機関一覧データ
                新型コロナワクチン接種医療機関オブジェクトのリストを要素に持つ
                オブジェクト

        """
        state = (
            "SELECT"
            + " "
            + "name,address,phone_number,book_at_medical_institution,"
            + "book_at_call_center,area,memo"
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
                "備考",
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
                        medical_institution.memo,
                    ]
                ]
            )
        return rows

    def get_name_list(self) -> list:
        """新型コロナワクチン接種医療機関の名称全件のリストを返す

        Returns:
            res (list): 医療機関の名称一覧リスト

        """
        state = "SELECT name FROM " + self.table_name + " ORDER BY id;"
        name_list = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    name_list.append(row["name"])
        return name_list

    def get_area_list(self) -> list:
        """新型コロナワクチン接種医療機関の地域全件のリストを返す

        Returns:
            res (list): 医療機関の地域一覧リスト

        """
        state = "SELECT DISTINCT(area) FROM " + self.table_name + " ORDER BY area;"
        area_list = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    area_list.append(row["area"])
        return area_list

    def get_locations(self, area: Optional[str] = None) -> list:
        """新型コロナワクチン接種医療機関の一覧に医療機関の位置情報を付けて返す

        Args:
            area (str): 医療機関の地区

        Returns:
            locations (list of tuple): 位置情報付き医療機関一覧データ
                新型コロナワクチン接種医療機関の情報に緯度経度を含めたタプルのリスト

        """
        state = (
            "SELECT"
            + " "
            + "name,address,phone_number,book_at_medical_institution,"
            + "book_at_call_center,memo,latitude,longitude"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "LEFT JOIN locations ON"
            + " "
            + self.table_name
            + ".name = locations.medical_institution_name"
        )
        if area:
            state = state + " WHERE area=%s"
        state = state + " ORDER BY " + self.table_name + ".id;"
        locations = list()
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                if area:
                    cur.execute(state, (area,))
                else:
                    cur.execute(state)
                for row in cur.fetchall():
                    locations.append(row)
        return locations
