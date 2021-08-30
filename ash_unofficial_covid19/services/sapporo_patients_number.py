from datetime import datetime, timedelta, timezone

from psycopg2.extras import DictCursor

from ash_unofficial_covid19.models.sapporo_patients_number import (
    SapporoPatientsNumberFactory
)
from ash_unofficial_covid19.services.service import Service


class SapporoPatientsNumberService(Service):
    """札幌市の新型コロナウイルス感染症日別新規患者数のデータを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "sapporo_patients_numbers")

    def create(self, sapporo_patients_numbers: SapporoPatientsNumberFactory) -> None:
        """データベースへ札幌市の新型コロナウイルス感染症日別新規患者数のデータを保存

        Args:
            sapporo_patients_numbers (:obj:`SapporoPatientsNumberFactory`): 患者数データ
                札幌市の新型コロナウイルス感染症日別新規患者数のデータのオブジェクトの
                リストを要素に持つオブジェクト

        """
        items = (
            "publication_date",
            "patients_number",
            "updated_at",
        )

        data_lists = list()
        for sapporo_patients_number in sapporo_patients_numbers.items:
            data_lists.append(
                [
                    sapporo_patients_number.publication_date,
                    sapporo_patients_number.patients_number,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="publication_date",
            data_lists=data_lists,
        )

    def find_all(self) -> SapporoPatientsNumberFactory:
        """札幌市の新型コロナウイルス感染症日別新規患者数のデータの全件リストを返す

        Returns:
            res (:obj:`SapporoPatientsNumberFactory`): 日別新規患者数のデータ一覧
                札幌市の新型コロナウイルス感染症日別新規患者数データのオブジェクトの
                リストを要素に持つオブジェクト

        """
        state = (
            "SELECT"
            + " "
            + "publication_date,patients_number"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY publication_date DESC"
            + ";"
        )
        factory = SapporoPatientsNumberFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory
