from datetime import date, datetime, timedelta, timezone
from typing import Optional

import psycopg2
from psycopg2.extras import DictCursor

from ..errors import ServiceError
from ..models.patients_number import PatientsNumberFactory
from ..services.service import Service


class PatientsNumberService(Service):
    """旭川市の新型コロナウイルス感染症日別年代別陽性患者数データを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "patients_numbers")

    def create(self, patients_numbers: PatientsNumberFactory) -> None:
        """データベースへ新型コロナウイルス感染症日別年代別陽性患者数データを一括登録

        Args:
            patients_number (:obj:`PatientsNumberFactory`): 陽性患者数データリスト
                日別年代別陽性患者数データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
            "publication_date",
            "age_under_10",
            "age_10s",
            "age_20s",
            "age_30s",
            "age_40s",
            "age_50s",
            "age_60s",
            "age_70s",
            "age_80s",
            "age_over_90",
            "investigating",
            "updated_at",
        )

        # バルクインサートするデータのリストを作成
        data_lists = list()
        for patients_number in patients_numbers.items:
            data_lists.append(
                [
                    patients_number.publication_date,
                    patients_number.age_under_10,
                    patients_number.age_10s,
                    patients_number.age_20s,
                    patients_number.age_30s,
                    patients_number.age_40s,
                    patients_number.age_50s,
                    patients_number.age_60s,
                    patients_number.age_70s,
                    patients_number.age_80s,
                    patients_number.age_over_90,
                    patients_number.investigating,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="publication_date",
            data_lists=data_lists,
        )

    def delete(self, publication_date: date) -> bool:
        """指定した報道発表日の日別年代別陽性患者数データを削除する

        Args:
            publication_date (date): 削除するデータの報道発表日

        Returns:
            bool: データ削除に成功したら真を返す

        """
        if not isinstance(publication_date, date):
            raise ServiceError("報道発表日の指定に誤りがあります。")

        state = "DELETE from" + " " + self.table_name + " " + "WHERE publication_date = %s;"
        values = (publication_date,)
        result = False
        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(state, values)
                    if cur.statusmessage == "DELETE 1":
                        result = True
                        self.info_log(publication_date.strftime("%Y-%m-%d") + "のデータを削除しました。")
                    else:
                        self.error_log(publication_date.strftime("%Y-%m-%d") + "のデータを削除できませんでした。")
            except (
                psycopg2.DataError,
                psycopg2.IntegrityError,
                psycopg2.InternalError,
            ) as e:
                self.error_log(e.args[0])
                raise ServiceError("日別年代別陽性患者数データの削除に失敗しました。")

        return result

    def find(self, publication_date: Optional[date] = None) -> PatientsNumberFactory:
        """新型コロナウイルス感染症日別年代別患者数の全件を返す

        引数を指定しない場合、全件データを返す。

        Args:
            publication_date (date): 検索するデータの報道発表日

        Returns:
            res (:obj:`PatientsNumberFactory`): 日別年代別陽性患者数データ
                新型コロナウイルス感染症患者オブジェクトの全件リストを要素に持つ
                オブジェクト

        """
        if publication_date is None:
            target_date_list = None
        else:
            if isinstance(publication_date, date):
                target_date_list = [
                    publication_date.strftime("%Y-%m-%d"),
                ]
            else:
                raise ServiceError("報道発表日の指定に誤りがあります。")

        state = (
            "SELECT"
            + " "
            + "publication_date,age_under_10,age_10s,age_20s,age_30s,age_40s,age_50s,"
            + "age_60s,age_70s,age_80s,age_over_90,investigating"
            + " "
            + "FROM"
            + " "
            + self.table_name
        )
        where_sentence = " " + "WHERE publication_date = %s"
        order_sentence = " " + "ORDER BY publication_date ASC;"
        factory = PatientsNumberFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                if publication_date is None:
                    cur.execute(state + order_sentence)
                else:
                    cur.execute(state + where_sentence + order_sentence, target_date_list)

                for dict_cursor in cur.fetchall():
                    factory.create(**dict(dict_cursor))

        return factory

    def get_rows(self) -> list:
        """日別年代別陽性患者数データをリストを返す

        Returns:
            rows (list of list): 日別年代別陽性患者数データの二次元配列

        """
        patients_numbers = self.find()
        rows = list()
        for patients_number in patients_numbers.items:
            publication_date = patients_number.publication_date.strftime("%Y-%m-%d")
            rows.append(
                [
                    str(v) if isinstance(v, int) else v
                    for v in [
                        publication_date,
                        patients_number.age_under_10,
                        patients_number.age_10s,
                        patients_number.age_20s,
                        patients_number.age_30s,
                        patients_number.age_40s,
                        patients_number.age_50s,
                        patients_number.age_60s,
                        patients_number.age_70s,
                        patients_number.age_80s,
                        patients_number.age_over_90,
                        patients_number.investigating,
                    ]
                ]
            )

        return rows
