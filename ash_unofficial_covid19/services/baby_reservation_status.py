from datetime import datetime, timedelta, timezone
from typing import Optional

import psycopg2

from ..errors import ServiceError
from ..models.baby_reservation_status import BabyReservationStatusFactory, BabyReservationStatusLocationFactory
from ..services.database import ConnectionPool
from ..services.service import Service


class BabyReservationStatusService(Service):
    """旭川市新型コロナ接種医療機関の予約受付状況データを扱うサービス"""

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        table_name = "baby_reservation_statuses"
        Service.__init__(self, table_name, pool)

    def create(self, baby_reservation_statuses: BabyReservationStatusFactory) -> None:
        """データベースへ新型コロナワクチン接種医療機関の予約受付状況データを保存

        Args:
            baby_reservation_statuses (:obj:`BabyReservationStatusFactory`): 予約受付状況データ
                医療機関の予約受付状況データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
            "area",
            "medical_institution_name",
            "address",
            "phone_number",
            "vaccine",
            "status",
            "inoculation_time",
            "target_age",
            "is_target_family",
            "is_target_not_family",
            "is_target_suberb",
            "target_other",
            "memo",
            "updated_at",
        )

        data_lists = list()
        for reservation_status in baby_reservation_statuses.items:
            data_lists.append(
                [
                    reservation_status.area,
                    reservation_status.medical_institution_name,
                    reservation_status.address,
                    reservation_status.phone_number,
                    reservation_status.vaccine,
                    reservation_status.status,
                    reservation_status.inoculation_time,
                    reservation_status.target_age,
                    reservation_status.is_target_family,
                    reservation_status.is_target_not_family,
                    reservation_status.is_target_suberb,
                    reservation_status.target_other,
                    reservation_status.memo,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="medical_institution_name,vaccine",
            data_lists=data_lists,
        )

    def delete(self, target_values: tuple) -> bool:
        """指定した主キーの値を持つデータを削除する

        Args:
            target_value (tuple): 削除対象の医療機関名とワクチン種類のタプル

        Returns:
            result (bool): 削除に成功したら真を返す

        """
        if not isinstance(target_values, tuple):
            raise TypeError("キーの指定がタプルになっていません。")
        else:
            if len(target_values) == 2:
                for target_value in target_values:
                    if not isinstance(target_value, str):
                        raise TypeError("キーの指定が文字列ではありません。")
            else:
                raise ServiceError("キーの指定の指定の配列の要素数が正しくありません。")

        state = "DELETE FROM " + self.table_name + " " + "WHERE medical_institution_name=%s" + " " + "AND vaccine=%s;"
        log_message = (
            self.table_name + "テーブルから" + " " + str(target_values[0]) + ", " + str(target_values[1]) + " " + "を"
        )
        try:
            with self.get_connection() as cur:
                cur.execute(state, target_values)
                result = cur.rowcount
            if result:
                self.info_log(log_message + "削除しました。")
                return True
            else:
                self.error_log(log_message + "削除できませんでした。")
                return False
        except (
            psycopg2.DataError,
            psycopg2.IntegrityError,
            psycopg2.InternalError,
        ) as e:
            self.error_log(log_message + "削除できませんでした。")
            raise ServiceError(e.args[0])

    def get_medical_institution_list(self) -> list:
        """新型コロナワクチン接種医療機関一覧を取得

        Returns:
            medical_institution_list (list of tuple): 医療機関の一覧リスト
                新型コロナワクチン接種医療機関の名称、ワクチン種類のタプルを
                リストで返す。

        """
        state = (
            "SELECT DISTINCT ON (medical_institution_name,vaccine)"
            + " "
            + "medical_institution_name,vaccine"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY medical_institution_name,vaccine;"
        )
        medical_institution_list = list()
        with self.get_connection() as cur:
            cur.execute(state)
            for row in cur.fetchall():
                medical_institution_list.append((row["medical_institution_name"], row["vaccine"]))

        return medical_institution_list

    def get_dicts(self) -> dict:
        """新型コロナワクチン接種医療機関予約状況を辞書で返す

        Returns:
            dicts (dict): 新型コロナワクチン接種医療機関予約受付状況の辞書

        """
        state = (
            "SELECT "
            + "area,medical_institution_name,"
            + "address,phone_number,vaccine,status,inoculation_time,target_age,"
            + "is_target_family,is_target_not_family,is_target_suberb,target_other,memo "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY area,address,vaccine;"
        )
        dicts = dict()
        with self.get_connection() as cur:
            cur.execute(state)
            i = 0
            for row in cur.fetchall():
                # 医療機関名とワクチンの種類で複合キーとなっているが分かりにくいので
                # 仮の連番をキーに採用する。
                key = "row" + str(i)
                value = dict(row)
                dicts[key] = value
                i += 1

        return dicts

    def find(
        self, medical_institution_name: Optional[str] = None, area: Optional[str] = None
    ) -> BabyReservationStatusLocationFactory:
        """新型コロナワクチン接種医療機関予約状況と位置情報の検索

        指定した新型コロナワクチン接種医療機関の予約受付状況と位置情報を返す

        Args:
            medical_institution_name (str): 医療機関の名称
            area (str): 地区

        Returns:
            results (list of :obj:`BabyReservationStatusLocation`): 予約受付状況詳細データ
                新型コロナワクチン接種医療機関予約受付状況の情報に緯度経度を含めた
                データオブジェクトのリスト。

        """
        search_args = list()
        where_sentence = ""
        if medical_institution_name is not None:
            if isinstance(medical_institution_name, str):
                where_sentence += " " + "WHERE reserve.medical_institution_name=%s"
                search_args.append(medical_institution_name)
            else:
                raise TypeError("医療機関名の指定に誤りがあります。")

        if area is not None:
            if isinstance(area, str):
                if len(search_args) == 0:
                    where_sentence += " " + "WHERE"
                else:
                    where_sentence += " " + "AND"
                where_sentence += " " + "area=%s"
                search_args.append(area)
            else:
                raise TypeError("地区の指定に誤りがあります。")

        state = (
            "SELECT "
            + "area,reserve.medical_institution_name,"
            + "address,phone_number,vaccine,status,inoculation_time,target_age,"
            + "is_target_family,is_target_not_family,is_target_suberb,target_other,"
            + "latitude,longitude,memo "
            + "FROM "
            + self.table_name
            + " "
            + "AS reserve"
            + " "
            + "LEFT JOIN locations AS loc ON reserve.medical_institution_name="
            + "loc.medical_institution_name"
        )
        order_sentence = " " + "ORDER BY area,address,vaccine;"
        factory = BabyReservationStatusLocationFactory()
        with self.get_connection() as cur:
            if len(search_args) == 0:
                cur.execute(state + order_sentence)
            else:
                cur.execute(state + where_sentence + order_sentence, search_args)
            for row in cur.fetchall():
                factory.create(**row)

        return factory

    def get_area_list(self) -> list:
        """新型コロナワクチン接種医療機関の地区一覧を取得

        Returns:
            area_list (list): 医療機関の地区一覧リスト

        """
        state = "SELECT DISTINCT(area)" + " " + "FROM" + " " + self.table_name + " " + "ORDER BY area;"
        area_list = list()
        with self.get_connection() as cur:
            cur.execute(state)
            for row in cur.fetchall():
                area_list.append(row["area"])

        return area_list
