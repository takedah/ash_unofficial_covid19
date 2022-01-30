from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

import pandas as pd
import psycopg2
from psycopg2.extras import DictCursor

from ..config import Config
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

    def get_aggregate_by_days(self, from_date: date, to_date: date) -> list:
        """指定した期間の1日ごとの陽性患者数の集計結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            aggregate_by_days (list of tuple): 集計結果
                1日ごとの日付とその週の新規陽性患者数を要素とするタプル

        """
        if not isinstance(from_date, date) or not isinstance(to_date, date):
            raise ServiceError("期間の範囲指定が日付になっていません。")

        state = (
            "SELECT date(from_day) AS publication_date, "
            + "("
            + "SUM(age_under_10) + SUM(age_10s) + SUM(age_20s) + SUM(age_30s) + "
            + "SUM(age_40s) + SUM(age_50s) + SUM(age_60s) + SUM(age_70s) + "
            + "SUM(age_80s) + SUM(age_over_90) + SUM(investigating)"
            + ") "
            + "AS patients_number FROM "
            + "(SELECT generate_series AS from_day, "
            + "generate_series + '1 day'::interval AS to_day FROM "
            + "generate_series(%s::DATE, %s::DATE, '1 day')) "
            + "AS day_ranges LEFT JOIN patients_numbers ON "
            + "from_day <= patients_numbers.publication_date AND "
            + "patients_numbers.publication_date < to_day GROUP BY from_day "
            + "ORDER BY publication_date;"
        )
        aggregate_by_days = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
                for row in cur.fetchall():
                    publication_date = row["publication_date"]
                    if row["patients_number"] is None:
                        patients_number = 0
                    else:
                        patients_number = row["patients_number"]
                    aggregate_by_days.append((publication_date, patients_number))
        return aggregate_by_days

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
            + "("
            + "SUM(age_under_10) + SUM(age_10s) + SUM(age_20s) + SUM(age_30s) + "
            + "SUM(age_40s) + SUM(age_50s) + SUM(age_60s) + SUM(age_70s) + "
            + "SUM(age_80s) + SUM(age_over_90) + SUM(investigating)"
            + ") "
            + "AS patients_number FROM "
            + "(SELECT generate_series AS from_week, "
            + "generate_series + '7 days'::interval AS to_week FROM "
            + "generate_series(%s::DATE, %s::DATE, '7 days')) "
            + "AS week_ranges LEFT JOIN patients_numbers ON "
            + "from_week <= patients_numbers.publication_date AND "
            + "patients_numbers.publication_date < to_week GROUP BY from_week "
            + "ORDER BY weeks;"
        )
        aggregate_by_weeks = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
                for row in cur.fetchall():
                    weeks = row["weeks"]
                    if row["patients_number"] is None:
                        patients_number = 0
                    else:
                        patients_number = row["patients_number"]
                    aggregate_by_weeks.append((weeks, patients_number))
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
        for week_data in aggregate_by_weeks:
            per_hundred_thousand_population = float(
                Decimal(str(week_data[1] / Config.POPULATION * 100000)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            per_hundred_thousand_population_per_week.append((week_data[0], per_hundred_thousand_population))
        return per_hundred_thousand_population_per_week

    def get_aggregate_by_weeks_per_age(self, from_date: date, to_date: date) -> pd.DataFrame:
        """指定した期間の1週間ごとの年代別の陽性患者数の集計結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            aggregate_by_weeks (:obj:`pd.DataFrame`): 集計結果
                1週間ごとの日付とその週の年代別新規陽性患者数をpandasのDataFrameで返す

        """
        if not isinstance(from_date, date) or not isinstance(to_date, date):
            raise ServiceError("期間の範囲指定が日付になっていません。")

        state = (
            "SELECT date(from_week) AS weeks, "
            + "SUM(age_under_10) AS age_under_10, SUM(age_10s) AS age_10s, "
            + "SUM(age_20s) AS age_20s, SUM(age_30s) AS age_30s, "
            + "SUM(age_40s) AS age_40s, SUM(age_50s) AS age_50s, "
            + "SUM(age_60s) AS age_60s, SUM(age_70s) AS age_70s, "
            + "SUM(age_80s) AS age_80s, SUM(age_over_90) AS age_over_90, "
            + "SUM(investigating) AS investigating "
            + "FROM "
            + "(SELECT generate_series AS from_week, "
            + "generate_series + '7 days'::interval AS to_week FROM "
            + "generate_series(%s::DATE, %s::DATE, '7 days')) "
            + "AS week_ranges LEFT JOIN patients_numbers ON "
            + "from_week <= patients_numbers.publication_date AND "
            + "patients_numbers.publication_date < to_week GROUP BY from_week "
            + "ORDER BY weeks;"
        )
        df = pd.DataFrame(
            columns=[
                "10歳未満",
                "10代",
                "20代",
                "30代",
                "40代",
                "50代",
                "60代",
                "70代",
                "80代",
                "90歳以上",
                "調査中等",
            ]
        )
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
                for row in cur.fetchall():
                    df.at[row["weeks"], "10歳未満"] = row["age_under_10"]
                    df.at[row["weeks"], "10代"] = row["age_10s"]
                    df.at[row["weeks"], "20代"] = row["age_20s"]
                    df.at[row["weeks"], "30代"] = row["age_30s"]
                    df.at[row["weeks"], "40代"] = row["age_40s"]
                    df.at[row["weeks"], "50代"] = row["age_50s"]
                    df.at[row["weeks"], "60代"] = row["age_60s"]
                    df.at[row["weeks"], "70代"] = row["age_70s"]
                    df.at[row["weeks"], "80代"] = row["age_80s"]
                    df.at[row["weeks"], "90歳以上"] = row["age_over_90"]
                    df.at[row["weeks"], "調査中等"] = row["investigating"]

        df.fillna(0, inplace=True)
        return df.fillna(0)

    def get_patients_number_by_age(self, from_date: date, to_date: date) -> list:
        """年代別の陽性患者数を返す

        Args:
            from_date (obj:`date`): 累計の始期
            to_date (obj:`date`): 累計の終期

        Returns:
            patients_number_by_age (list of tuple): 集計結果
                年代別の陽性患者数を要素とするタプルのリスト

        """
        if not isinstance(from_date, date) or not isinstance(to_date, date):
            raise ServiceError("期間の範囲指定が日付になっていません。")

        # 調査中等は集計しない。
        state = (
            "SELECT "
            + "SUM(age_under_10) AS age_under_10, SUM(age_10s) AS age_10s, "
            + "SUM(age_20s) AS age_20s, SUM(age_30s) AS age_30s, "
            + "SUM(age_40s) AS age_40s, SUM(age_50s) AS age_50s, "
            + "SUM(age_60s) AS age_60s, SUM(age_70s) AS age_70s, "
            + "SUM(age_80s) AS age_80s, SUM(age_over_90) AS age_over_90 "
            + "FROM patients_numbers WHERE DATE(publication_date) "
            + "BETWEEN %s AND %s;"
        )
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
                for row in cur.fetchall():
                    patients_number_by_age = [
                        ("10歳未満", row["age_under_10"]),
                        ("10代", row["age_10s"]),
                        ("20代", row["age_20s"]),
                        ("30代", row["age_30s"]),
                        ("40代", row["age_40s"]),
                        ("50代", row["age_50s"]),
                        ("60代", row["age_60s"]),
                        ("70代", row["age_70s"]),
                        ("80代", row["age_80s"]),
                        ("90歳以上", row["age_over_90"]),
                    ]
        return patients_number_by_age

    def get_total_by_months(self, from_date: date, to_date: date) -> list:
        """指定した期間の1か月ごとの陽性患者数の累計結果を返す

        Args:
            from_date (obj:`date`): 累計の始期
            to_date (obj:`date`): 累計の終期

        Returns:
            total_by_months (list of tuple): 集計結果
                1か月ごとの年月とその週までの累計陽性患者数を要素とするタプルのリスト

        """
        if not isinstance(from_date, date) or not isinstance(to_date, date):
            raise ServiceError("期間の範囲指定が日付になっていません。")

        state = (
            "SELECT date(aggregate_patients.from_month) AS month, "
            + "SUM(aggregate_patients.patients_number) OVER("
            + "ORDER BY aggregate_patients.from_month) AS total_patients FROM "
            + "("
            + "SELECT from_month, "
            + "("
            + "SUM(age_under_10) + SUM(age_10s) + SUM(age_20s) + SUM(age_30s) + "
            + "SUM(age_40s) + SUM(age_50s) + SUM(age_60s) + SUM(age_70s) + "
            + "SUM(age_80s) + SUM(age_over_90) + SUM(investigating)"
            + ") "
            + "AS patients_number FROM "
            + "("
            + "SELECT generate_series AS from_month, generate_series + "
            + "'1 months'::interval AS to_month FROM generate_series(%s::DATE, %s::DATE, '1 months')"
            + ") AS month_ranges "
            + "LEFT JOIN patients_numbers "
            + "ON from_month <= patients_numbers.publication_date AND "
            + "patients_numbers.publication_date < to_month GROUP BY from_month"
            + ") AS aggregate_patients;"
        )
        total_by_months = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
                for row in cur.fetchall():
                    month = row["month"]
                    if row["total_patients"] is None:
                        total_patients = 0
                    else:
                        total_patients = int(row["total_patients"])
                    total_by_months.append((month, total_patients))
        return total_by_months
