from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from ..config import Config
from ..errors import ServiceError
from ..models.sapporo_patients_number import SapporoPatientsNumberFactory
from ..services.database import ConnectionPool
from ..services.service import Service


class SapporoPatientsNumberService(Service):
    """札幌市の新型コロナウイルス感染症日別新規患者数のデータを扱うサービス"""

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        Service.__init__(self, "sapporo_patients_numbers", pool)

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
        with self.get_connection() as cur:
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
        if not isinstance(from_date, date) or not isinstance(to_date, date):
            raise ServiceError("期間の範囲指定が日付になっていません。")

        state = (
            "SELECT date(from_week) AS weeks, "
            + "SUM(patients_number) AS patients FROM "
            + "(SELECT generate_series AS from_week, "
            + "generate_series + '7 days'::interval AS to_week FROM "
            + "generate_series(%s::DATE, %s::DATE, '7 days')) "
            + "AS week_ranges "
            + "LEFT JOIN "
            + self.table_name
            + " "
            + "ON from_week <= "
            + self.table_name
            + ".publication_date AND "
            + self.table_name
            + ".publication_date < to_week GROUP BY from_week "
            + "ORDER BY weeks;"
        )
        aggregate_by_weeks = list()
        with self.get_connection() as cur:
            cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
            for row in cur.fetchall():
                aggregate_by_weeks.append((row["weeks"], row["patients"]))

        return aggregate_by_weeks

    def get_per_hundred_thousand_population_per_week(self, from_date: date, to_date: date) -> list:
        """1週間の人口10万人あたりの新規陽性患者数の計算結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            per_hundred_thousand (list of tuple): 集計結果
                1週間ごとの日付とその週の人口10万人あたり新規陽性患者数を要素とする
                タプルのリスト
        """
        aggregate_by_weeks = self.get_aggregate_by_weeks(from_date=from_date, to_date=to_date)
        per_hundred_thousand_population_per_week = list()
        for aggregate in aggregate_by_weeks:
            if aggregate[1] is None:
                patients_number = 0
            else:
                patients_number = aggregate[1]
            target_week = aggregate[0]
            per_hundred_thousand_population = float(
                Decimal(str(patients_number / Config.SAPPORO_POPULATION * 100000)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            per_hundred_thousand_population_per_week.append((target_week, per_hundred_thousand_population))
        return per_hundred_thousand_population_per_week

    def get_last_update_date(self) -> date:
        """札幌市のオープンデータの最新の公表日を取得する

        Returns:
            last_update_date (date): 札幌市のオープンデータの最新の公表日を取得する

        """
        state = "SELECT MAX(publication_date) FROM " + self.table_name + ";"
        with self.get_connection() as cur:
            cur.execute(state)
            for row in cur.fetchall():
                last_update_date = row["max"]

        return last_update_date
