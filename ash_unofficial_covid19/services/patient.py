from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

import pandas as pd
import psycopg2
from dateutil.relativedelta import relativedelta

from ..config import Config
from ..errors import ServiceError
from ..models.patient import AsahikawaPatientFactory, HokkaidoPatientFactory
from ..services.database import ConnectionPool
from ..services.service import Service


class AsahikawaPatientService(Service):
    """旭川市の公表する新型コロナウイルス感染症患者データを扱うサービス"""

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        Service.__init__(self, "asahikawa_patients", pool)

    def create(self, patients: AsahikawaPatientFactory) -> None:
        """データベースへ新型コロナウイルス感染症患者データを一括登録する

        Args:
            patients (:obj:`AsahikawaPatientFactory`): 患者データリスト
                患者データのオブジェクトのリストを要素に持つオブジェクト

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

        # データベースへ登録処理
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
        try:
            with self.get_connection() as cur:
                cur.execute(state, values)
                if cur.statusmessage == "DELETE 1":
                    result = True

            self.info_log("市内番号" + str(patient_number) + "を削除しました。")
        except (
            psycopg2.DataError,
            psycopg2.IntegrityError,
            psycopg2.InternalError,
        ) as e:
            self.error_log(e.args[0])
            raise ServiceError("陽性患者データを削除できませんでした。")

        return result

    def find_all(self) -> AsahikawaPatientFactory:
        """新型コロナウイルス感染症患者の全件を返す

        Returns:
            res (:obj:`AsahikawaPatientFactory`): 患者データリストデータ
                新型コロナウイルス感染症患者オブジェクトの全件リストを要素に持つ
                オブジェクト

        """
        state = (
            "SELECT"
            + " "
            + "a.patient_number,a.city_code,a.prefecture,a.city_name,"
            + "a.publication_date,"
            + "h.onset_date,a.residence,a.age,a.sex,h.occupation as h_occupation,"
            + "a.occupation as a_occupation,h.status,h.symptom,"
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
        with self.get_connection() as cur:
            cur.execute(state)
            for dict_cursor in cur.fetchall():
                row = dict(dict_cursor)
                # 北海道データがない場合、職業は旭川データの値をセット
                if row["h_occupation"] is None:
                    row["occupation"] = row["a_occupation"]
                else:
                    row["occupation"] = row["h_occupation"]
                del row["h_occupation"], row["a_occupation"]
                factory.create(**row)

        return factory

    def find(self, page: int = 1, desc: bool = True) -> tuple[AsahikawaPatientFactory, int]:
        """新型コロナウイルス感染症患者データのリストをページネーション用に分割して返す

        Args:
            page (int): 検索結果を分割する場合、何番目の分割結果か数値で指定
            desc (bool): 降順にする場合Trueを指定

        Returns:
            res (tuple): ページネーションデータ
                AsahikawaPatientFactoryオブジェクトと
                ページネーションした場合の最大ページ数の数値を要素に持つタプル

        """
        if not isinstance(page, int):
            raise ServiceError("検索結果のページ指定に誤りがあります。")

        pagenation_option = ""
        max_page = 1

        count_state = "SELECT" + " " + "count(patient_number)" + " " + "FROM" + " " + self.table_name + ";"
        with self.get_connection() as cur:
            cur.execute(count_state)
            res = cur.fetchone()

        results_number = res["count"]
        # 検索結果の最大ページ数を取得
        max_view_number = 100
        if results_number < max_view_number:
            max_page = 1
        else:
            if divmod(results_number, max_view_number)[1] == 0:
                max_page = divmod(results_number, max_view_number)[0]
            else:
                max_page = divmod(results_number, max_view_number)[0] + 1

        # 指定されたページ数の検索結果を表示するためにスキップするレコード数を取得
        if max_page < page:
            raise ServiceError("指定したページ数が上限を超えています。")
        else:
            skip_record_number = (page - 1) * max_view_number

        # ページネーション用の追加SQL文字列を生成
        pagenation_option = " LIMIT " + str(max_view_number)
        if 1 < page:
            pagenation_option += " OFFSET " + str(skip_record_number)

        if desc:
            order = "DESC"
        else:
            order = "ASC"

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
            + "ORDER BY a.patient_number"
            + " "
            + order
        )
        state += pagenation_option + ";"
        factory = AsahikawaPatientFactory()
        with self.get_connection() as cur:
            cur.execute(state)
            for row in cur.fetchall():
                factory.create(**row)

        return (factory, max_page)

    def get_rows(self) -> list:
        """陽性患者属性データをリストを返す

        Returns:
            rows (list of list): 陽性患者属性データの二次元配列

        """
        patients = self.find_all()
        rows = list()
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

    def get_aggregate_by_days_per_age(self, from_date: date, to_date: date) -> list:
        """指定した期間の1日ごとの年代別陽性患者数の集計結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            aggregate_by_days_per_age (list of dict): 集計結果
                1日ごとの日付とその日の年代別新規陽性患者数を要素とする辞書のリスト

        """
        if not isinstance(from_date, date) or not isinstance(to_date, date):
            raise ServiceError("期間の範囲指定が日付になっていません。")

        state = (
            "SELECT date(from_day) AS publication_date, "
            + "COUNT(CASE WHEN age = '10歳未満' THEN TRUE ELSE NULL END) AS age_under_10, "
            + "COUNT(CASE WHEN age = '10代' THEN TRUE ELSE NULL END) AS age_10s, "
            + "COUNT(CASE WHEN age = '20代' THEN TRUE ELSE NULL END) AS age_20s, "
            + "COUNT(CASE WHEN age = '30代' THEN TRUE ELSE NULL END) AS age_30s, "
            + "COUNT(CASE WHEN age = '40代' THEN TRUE ELSE NULL END) AS age_40s, "
            + "COUNT(CASE WHEN age = '50代' THEN TRUE ELSE NULL END) AS age_50s, "
            + "COUNT(CASE WHEN age = '60代' THEN TRUE ELSE NULL END) AS age_60s, "
            + "COUNT(CASE WHEN age = '70代' THEN TRUE ELSE NULL END) AS age_70s, "
            + "COUNT(CASE WHEN age = '80代' THEN TRUE ELSE NULL END) AS age_80s, "
            + "COUNT(CASE WHEN age = '90歳以上' THEN TRUE ELSE NULL END) AS age_over_90, "
            + "COUNT(CASE WHEN age = '' THEN TRUE ELSE NULL END) AS investigating "
            + "FROM "
            + "(SELECT generate_series AS from_day, "
            + "generate_series + '1 day'::interval AS to_day FROM "
            + "generate_series(%s::DATE, %s::DATE, '1 day')) "
            + "AS day_ranges LEFT JOIN asahikawa_patients ON "
            + "from_day <= asahikawa_patients.publication_date AND "
            + "asahikawa_patients.publication_date < to_day GROUP BY from_day "
            + "ORDER BY from_day;"
        )
        aggregate_by_days_per_age = list()
        with self.get_connection() as cur:
            cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
            for row in cur.fetchall():
                aggregate_by_days_per_age.append(dict(row))

        return aggregate_by_days_per_age

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
            "SELECT date(from_day) AS days, "
            + "COUNT(DISTINCT patient_number) AS patients FROM "
            + "(SELECT generate_series AS from_day, "
            + "generate_series + '1 day'::interval AS to_day FROM "
            + "generate_series(%s::DATE, %s::DATE, '1 day')) "
            + "AS day_ranges LEFT JOIN asahikawa_patients ON "
            + "from_day <= asahikawa_patients.publication_date AND "
            + "asahikawa_patients.publication_date < to_day GROUP BY from_day;"
        )
        aggregate_by_days = list()
        with self.get_connection() as cur:
            cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
            for row in cur.fetchall():
                aggregate_by_days.append((row[0], row[1]))

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
            + "COUNT(DISTINCT patient_number) AS patients FROM "
            + "(SELECT generate_series AS from_week, "
            + "generate_series + '7 days'::interval AS to_week FROM "
            + "generate_series(%s::DATE, %s::DATE, '7 days')) "
            + "AS week_ranges LEFT JOIN asahikawa_patients ON "
            + "from_week <= asahikawa_patients.publication_date AND "
            + "asahikawa_patients.publication_date < to_week GROUP BY from_week;"
        )
        aggregate_by_weeks = list()
        with self.get_connection() as cur:
            cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
            for row in cur.fetchall():
                aggregate_by_weeks.append((row[0], row[1]))

        return aggregate_by_weeks

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
            "SELECT date(from_week) AS weeks, age, "
            + "COUNT(DISTINCT patient_number) AS patients FROM "
            + "(SELECT generate_series AS from_week, "
            + "generate_series + '7 days'::interval AS to_week FROM "
            + "generate_series(%s::DATE, %s::DATE, '7 days')) "
            + "AS week_ranges LEFT JOIN asahikawa_patients ON "
            + "from_week <= asahikawa_patients.publication_date AND "
            + "asahikawa_patients.publication_date < to_week GROUP BY from_week, age "
            + "ORDER BY weeks, age;"
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
                "非公表",
            ]
        )
        with self.get_connection() as cur:
            cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
            for row in cur.fetchall():
                if row["age"] is None:
                    df.loc[row["weeks"]] = 0
                elif row["age"] == "":
                    df.at[row["weeks"], "非公表"] = row["patients"]
                else:
                    df.at[row["weeks"], row["age"]] = row["patients"]

        return df.fillna(0)

    def get_seven_days_moving_average(self, from_date: date, to_date: date) -> list:
        """1日あたりの新規陽性患者数の7日間移動平均の計算結果を返す

        Args:
            from_date (obj:`date`): 集計の始期
            to_date (obj:`date`): 集計の終期

        Returns:
            seven_days_moving_average (list of tuple): 集計結果
                1週間ごとの日付とその週の1日あたり平均新規陽性患者数を要素とする
                タプルのリスト
        """
        aggregate_by_weeks = self.get_aggregate_by_weeks(from_date=from_date, to_date=to_date)
        seven_days_moving_average = list()
        for patients_number in aggregate_by_weeks:
            moving_average = float(
                Decimal(str(patients_number[1] / 7)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )
            seven_days_moving_average.append((patients_number[0], moving_average))
        return seven_days_moving_average

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
        for patients_number in aggregate_by_weeks:
            per_hundred_thousand_population = float(
                Decimal(str(patients_number[1] / Config.POPULATION * 100000)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
            per_hundred_thousand_population_per_week.append((patients_number[0], per_hundred_thousand_population))
        return per_hundred_thousand_population_per_week

    def get_reproduction_number(self, to_date: date) -> float:
        """指定した日時点の実効再生産数の簡易推定値を算出

        国立感染症研究所の「COVID-19感染報告者数に基づく簡易実効再生産数推定方法」に基づき計算している。
        https://www.niid.go.jp/niid/ja/diseases/ka/corona-virus/2019-ncov/2502-idsc/iasr-in/10465-496d04.html

        Args:
            to_date (obj:`date`): 集計の終期

        Returns:
            reproduction_number (float): 実効再生産数

        """
        generation_time = 5
        from_date = to_date - relativedelta(days=6 + generation_time)
        aggregate_by_days = self.get_aggregate_by_days(from_date=from_date, to_date=to_date)
        latest_number = 0
        generation_time_before_number = 0
        i = 0
        for patients_number in aggregate_by_days:
            if i < 5:
                generation_time_before_number += patients_number[1]
            elif 5 <= i and i < 7:
                generation_time_before_number += patients_number[1]
                latest_number += patients_number[1]
            else:
                latest_number += patients_number[1]
            i += 1

        if generation_time_before_number == 0:
            return 0

        return float(
            Decimal(str(latest_number / generation_time_before_number)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )

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
            "SELECT date(aggregate_patients.from_month), "
            + "SUM(aggregate_patients.patients) OVER("
            + "ORDER BY aggregate_patients.from_month) AS total_patients FROM "
            + "("
            + "SELECT from_month, COUNT(DISTINCT patient_number) as patients FROM "
            + "("
            + "SELECT generate_series AS from_month, generate_series + "
            + "'1 months'::interval AS to_month FROM generate_series(%s::DATE, %s::DATE, '1 months')"
            + ") AS month_ranges "
            + "LEFT JOIN asahikawa_patients "
            + "ON from_month <= asahikawa_patients.publication_date AND "
            + "asahikawa_patients.publication_date < to_month GROUP BY from_month"
            + ") AS aggregate_patients;"
        )
        total_by_months = list()
        with self.get_connection() as cur:
            cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
            for row in cur.fetchall():
                total_by_months.append((row[0], row[1]))

        return total_by_months

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

        state = (
            "SELECT age,COUNT(age) FROM asahikawa_patients WHERE DATE(publication_date) "
            + "BETWEEN %s AND %s GROUP BY age ORDER BY age;"
        )
        patients_number_by_age = [
            ("10歳未満", 0),
            ("10代", 0),
            ("20代", 0),
            ("30代", 0),
            ("40代", 0),
            ("50代", 0),
            ("60代", 0),
            ("70代", 0),
            ("80代", 0),
            ("90歳以上", 0),
        ]
        with self.get_connection() as cur:
            cur.execute(state, (from_date.strftime("%Y-%m-%d"), to_date.strftime("%Y-%m-%d")))
            for row in cur.fetchall():
                if row[0] == "10歳未満":
                    patients_number_by_age[0] = (row[0], row[1])
                elif row[0] == "10代":
                    patients_number_by_age[1] = (row[0], row[1])
                elif row[0] == "20代":
                    patients_number_by_age[2] = (row[0], row[1])
                elif row[0] == "30代":
                    patients_number_by_age[3] = (row[0], row[1])
                elif row[0] == "40代":
                    patients_number_by_age[4] = (row[0], row[1])
                elif row[0] == "50代":
                    patients_number_by_age[5] = (row[0], row[1])
                elif row[0] == "60代":
                    patients_number_by_age[6] = (row[0], row[1])
                elif row[0] == "70代":
                    patients_number_by_age[7] = (row[0], row[1])
                elif row[0] == "80代":
                    patients_number_by_age[8] = (row[0], row[1])
                elif row[0] == "90歳以上":
                    patients_number_by_age[9] = (row[0], row[1])

        return patients_number_by_age

    def get_patients_number(self, target_date: date) -> int:
        """指定した日の陽性患者数を返す

        Args:
            target_date (obj:`date`): 対象年月日

        Returns:
            patients_number (int): 対象年月日の陽性患者数

        """
        state = "SELECT COUNT(patient_number) FROM" + " " + self.table_name + " " + "WHERE publication_date = %s;"
        with self.get_connection() as cur:
            cur.execute(state, (target_date,))
            res = cur.fetchone()

        patients_number = res[0]
        if isinstance(patients_number, int):
            return patients_number
        else:
            return 0


class HokkaidoPatientService(Service):
    """北海道の公表する新型コロナウイルス感染症患者データを扱うサービス"""

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        Service.__init__(self, "hokkaido_patients", pool)

    def create(self, patients: HokkaidoPatientFactory) -> None:
        """データベースへ新型コロナウイルス感染症患者データを保存

        Args:
            patient (:obj:`HokkaidoPatientFactory`): 集計結果
                患者データのオブジェクトのリストを要素に持つオブジェクト

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

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="patient_number",
            data_lists=data_lists,
        )
