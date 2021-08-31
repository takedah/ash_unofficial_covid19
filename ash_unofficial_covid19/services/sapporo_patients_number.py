from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from psycopg2.extras import DictCursor

from ash_unofficial_covid19.config import Config
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

    def get_aggregate_by_weeks(self, from_date: date, to_date: date) -> list:
        """指定した期間の1週間ごとの陽性患者数の集計結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            aggregate_by_weeks (list of tuple): 集計結果
                1週間ごとの日付とその週の新規陽性患者数を要素とするタプルのリスト

        """
        state = (
            "SELECT date(from_week) AS weeks, "
            + "SUM(patients_number) AS patients FROM "
            + "(SELECT generate_series AS from_week, "
            + "generate_series + '7 days'::interval AS to_week FROM "
            + "generate_series('"
            + from_date.strftime("%Y-%m-%d")
            + "'::DATE, '"
            + to_date.strftime("%Y-%m-%d")
            + "'::DATE, '7 days')) "
            + "AS week_ranges "
            + "LEFT JOIN "
            + self.table_name
            + " "
            + "ON from_week <= "
            + self.table_name
            + ".publication_date AND "
            + self.table_name
            + ".publication_date < to_week GROUP BY from_week;"
        )
        aggregate_by_weeks = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    aggregate_by_weeks.append((row["weeks"], row["patients"]))
        return aggregate_by_weeks

    def get_per_hundred_thousand_population_per_week(
        self, from_date: date, to_date: date
    ) -> list:
        """1週間の人口10万人あたりの新規陽性患者数の計算結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            per_hundred_thousand (list of tuple): 集計結果
                1週間ごとの日付とその週の人口10万人あたり新規陽性患者数を要素とする
                タプルのリスト
        """
        aggregate_by_weeks = self.get_aggregate_by_weeks(
            from_date=from_date, to_date=to_date
        )
        per_hundred_thousand_population_per_week = list()
        for patients_number in aggregate_by_weeks:
            per_hundred_thousand_population = float(
                Decimal(
                    str(patients_number[1] / Config.SAPPORO_POPULATION * 100000)
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )
            per_hundred_thousand_population_per_week.append(
                (patients_number[0], per_hundred_thousand_population)
            )
        return per_hundred_thousand_population_per_week
