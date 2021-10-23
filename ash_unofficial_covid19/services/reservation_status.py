from datetime import datetime, timedelta, timezone

import psycopg2
from psycopg2.extras import DictCursor

from ..errors import ServiceError
from ..models.reservation_status import ReservationStatusFactory
from ..services.service import Service


class ReservationStatusService(Service):
    """旭川市新型コロナ接種医療機関の予約受付状況データを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "reservation_statuses")

    def create(self, reservation_statuses: ReservationStatusFactory) -> None:
        """データベースへ新型コロナワクチン接種医療機関の予約受付状況データを保存

        Args:
            reservation_statuses (:obj:`ReservationStatusFactory`): 予約受付状況データ
                医療機関の予約受付状況データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
            "medical_institution_name",
            "address",
            "phone_number",
            "status",
            "target",
            "inoculation_time",
            "memo",
            "updated_at",
        )

        data_lists = list()
        for reservation_status in reservation_statuses.items:
            data_lists.append(
                [
                    reservation_status.medical_institution_name,
                    reservation_status.address,
                    reservation_status.phone_number,
                    reservation_status.status,
                    reservation_status.target,
                    reservation_status.inoculation_time,
                    reservation_status.memo,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="medical_institution_name",
            data_lists=data_lists,
        )

    def delete(self, target_value: str) -> bool:
        """指定した主キーの値を持つデータを削除する

        Args:
            target_value (str): 削除対象の医療機関名

        Returns:
            result (bool): 削除に成功したら真を返す

        """
        if not isinstance(target_value, str):
            raise ServiceError("削除対象の指定が文字列になっていません。")

        state = "DELETE FROM " + self.table_name + " " + "WHERE medical_institution_name=%s;"
        log_message = self.table_name + "テーブルから " + target_value + " " + "を"
        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(state, (target_value,))
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

    def find_all(self) -> ReservationStatusFactory:
        """新型コロナワクチン接種医療機関の予約受付状況の全件リストを返す

        Returns:
            res (:obj:`ReservationStatusFactory`): 医療機関の予約受付状況一覧データ
                新型コロナワクチン接種医療機関の予約受付状況オブジェクトのリストを
                要素に持つオブジェクト

        """
        state = (
            "SELECT"
            + " "
            + "medical_institution_name,address,phone_number,status,target,"
            + "inoculation_time,memo"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY medical_institution_name;"
        )
        factory = ReservationStatusFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory

    def get_name_list(self) -> list:
        """予約受付状況テーブルにある新型コロナワクチン接種医療機関の名称全件のリストを返す

        Returns:
            res (list of tuple): 医療機関の予約受付状況の名称一覧リスト

        """
        state = (
            "SELECT DISTINCT ON (medical_institution_name) medical_institution_name "
            + "FROM "
            + self.table_name
            + " "
            + "ORDER BY medical_institution_name;"
        )
        name_list = list()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    name_list.append(row["medical_institution_name"])
        return name_list
