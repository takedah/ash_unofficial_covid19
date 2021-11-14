from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import DictCursor

from ..errors import ServiceError
from ..models.medical_institution import MedicalInstitutionFactory
from ..services.service import Service


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
            "target_age",
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
                    medical_institution.target_age,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="name,target_age",
            data_lists=data_lists,
        )

    def delete(self, target_value: tuple) -> bool:
        """指定した主キーの値を持つデータを削除する

        Args:
            target_value (tuple): 削除対象の医療機関名と対象年齢を要素とするタプル

        Returns:
            result (bool): 削除に成功したら真を返す

        """
        state = "DELETE FROM " + self.table_name + " " + "WHERE name = %s AND target_age = %s;"
        log_message = self.table_name + "テーブルから " + str(target_value[0]) + ", " + str(target_value[1]) + " " + "を"
        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(state, target_value)
                    result = cur.rowcount
                if result:
                    conn.commit()
                    self.info_log(log_message + "削除しました。")
                    return True
                else:
                    self.info_log(log_message + "削除できませんでした。")
                    return False
            except (
                psycopg2.DataError,
                psycopg2.IntegrityError,
                psycopg2.InternalError,
            ) as e:
                self.error_log(log_message + "削除できませんでした。")
                raise ServiceError(e.args[0])

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
            + "book_at_call_center,area,target_age,memo"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY target_age,area,address"
            + ";"
        )
        factory = MedicalInstitutionFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory

    def get_rows(self) -> list:
        """新型コロナワクチン接種医療機関一覧データをリストを返す

        Returns:
            rows (list of list): 新型コロナワクチン接種医療機関一覧データの二次元配列

        """
        medical_institutions = self.find_all()
        rows = list()
        for medical_institution in medical_institutions.items:
            if medical_institution.book_at_medical_institution is None:
                book_at_medical_institution = ""
            else:
                book_at_medical_institution = str(int(medical_institution.book_at_medical_institution))
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
                        medical_institution.target_age,
                        medical_institution.memo,
                    ]
                ]
            )
        return rows

    def get_name_lists(self) -> list:
        """新型コロナワクチン接種医療機関の名称と対象年齢全件のリストを返す

        Returns:
            res (list of tuple): 医療機関の名称と対象年齢一覧リスト

        """
        state = (
            "SELECT DISTINCT ON (name,target_age) name, target_age FROM " + self.table_name + " " + "ORDER BY name;"
        )
        name_lists = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    name_lists.append((row["name"], row["target_age"]))
        return name_lists

    def get_area_list(self, is_pediatric: bool = False) -> list:
        """指定した対象年齢の新型コロナワクチン接種医療機関の地域全件のリストを返す

        Args:
            is_pediatric (bool): 12歳から15歳までの接種医療機関の場合真を指定

        Returns:
            res (list): 医療機関の地域一覧リスト

        """
        state = "SELECT DISTINCT(area) FROM " + self.table_name + " " + "WHERE target_age=%s" + " ORDER BY area;"
        if is_pediatric:
            target_age = "12歳から15歳まで"
        else:
            target_age = "16歳以上"

        area_list = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (target_age,))
                for row in cur.fetchall():
                    area_list.append(row["area"])
        return area_list
