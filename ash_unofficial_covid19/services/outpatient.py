from datetime import datetime, timedelta, timezone
from typing import Optional

import psycopg2

from ..errors import ServiceError
from ..models.outpatient import OutpatientFactory, OutpatientLocationFactory
from ..services.database import ConnectionPool
from ..services.service import Service


class OutpatientService(Service):
    """旭川市新型コロナ発熱外来データを扱うサービス"""

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        table_name = "outpatients"
        Service.__init__(self, table_name, pool)

    def create(self, outpatients: OutpatientFactory) -> None:
        """データベースへ新型コロナ発熱外来データを保存

        Args:
            outpatients (:obj:`OutpatientFactory`): 発熱外来データ
                発熱外来データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
            "is_outpatient",
            "is_positive_patients",
            "public_health_care_center",
            "medical_institution_name",
            "city",
            "address",
            "phone_number",
            "is_target_not_family",
            "is_pediatrics",
            "mon",
            "tue",
            "wed",
            "thu",
            "fri",
            "sat",
            "sun",
            "is_face_to_face_for_positive_patients",
            "is_online_for_positive_patients",
            "is_home_visitation_for_positive_patients",
            "memo",
            "updated_at",
        )

        data_lists = list()
        for outpatient in outpatients.items:
            data_lists.append(
                [
                    outpatient.is_outpatient,
                    outpatient.is_positive_patients,
                    outpatient.public_health_care_center,
                    outpatient.medical_institution_name,
                    outpatient.city,
                    outpatient.address,
                    outpatient.phone_number,
                    outpatient.is_target_not_family,
                    outpatient.is_pediatrics,
                    outpatient.mon,
                    outpatient.tue,
                    outpatient.wed,
                    outpatient.thu,
                    outpatient.fri,
                    outpatient.sat,
                    outpatient.sun,
                    outpatient.is_face_to_face_for_positive_patients,
                    outpatient.is_online_for_positive_patients,
                    outpatient.is_home_visitation_for_positive_patients,
                    outpatient.memo,
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
            raise TypeError("キーの指定が文字列になっていません。")

        state = "DELETE FROM " + self.table_name + " " + "WHERE medical_institution_name=%s;"
        log_message = self.table_name + "テーブルから" + " " + target_value + " " + "を"
        target_values = list()
        target_values.append(target_value)
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
        """新型コロナ発熱外来一覧を取得

        Returns:
            medical_institution_list (list): 医療機関の一覧リスト
                新型コロナ発熱外来名をリストで返す。

        """
        state = (
            "SELECT medical_institution_name"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY medical_institution_name;"
        )
        medical_institution_list = list()
        with self.get_connection() as cur:
            cur.execute(state)
            for row in cur.fetchall():
                medical_institution_list.append(row["medical_institution_name"])

        return medical_institution_list

    def find(
        self,
        medical_institution_name: Optional[str] = None,
        is_pediatrics: Optional[bool] = None,
        is_target_not_family: Optional[bool] = None,
    ) -> OutpatientLocationFactory:
        """新型コロナ発熱外来と位置情報の検索

        指定した新型コロナ発熱外来と位置情報を返す

        Args:
            medical_institution_name (str): 医療機関の名称
            is_pediatrics (bool): 小児対応の可否
            is_target_not_family (bool): かかりつけ患者以外の診療の可否

        Returns:
            results (list of :obj:`OutpatientLocation`): 発熱外来詳細データ
                新型コロナ発熱外来の情報に緯度経度を含めたデータオブジェクトのリスト。

        """
        search_args = list()
        # 外来対応医療機関列が空欄の医療機関を除外する
        where_sentence = " " + "WHERE is_outpatient IS TRUE"
        if medical_institution_name is not None:
            if isinstance(medical_institution_name, str):
                where_sentence += " " + "AND reserve.medical_institution_name=%s"
                search_args.append(medical_institution_name)
            else:
                raise TypeError("医療機関名の指定に誤りがあります。")

        if is_pediatrics is not None:
            if isinstance(is_pediatrics, bool):
                where_sentence += " " + "AND reserve.is_pediatrics=%s"
                search_args.append(str(is_pediatrics))
            else:
                raise TypeError("小児対応の可否の指定に誤りがあります。")

        if is_target_not_family is not None:
            if isinstance(is_target_not_family, bool):
                where_sentence += " " + "AND reserve.is_target_not_family=%s"
                search_args.append(str(is_target_not_family))
            else:
                raise TypeError("かかりつけ患者以外の診療の可否の指定に誤りがあります。")

        state = (
            "SELECT "
            + "is_outpatient,is_positive_patients,public_health_care_center,"
            + "reserve.medical_institution_name,city,address,phone_number,is_target_not_family,"
            + "is_pediatrics,mon,tue,wed,thu,fri,sat,sun,"
            + "is_face_to_face_for_positive_patients,is_online_for_positive_patients,"
            + "is_home_visitation_for_positive_patients,memo,longitude,latitude "
            + "FROM "
            + self.table_name
            + " "
            + "AS reserve"
            + " "
            + "LEFT JOIN locations AS loc ON reserve.medical_institution_name="
            + "loc.medical_institution_name"
        )
        order_sentence = " " + "ORDER BY address;"
        factory = OutpatientLocationFactory()
        with self.get_connection() as cur:
            if len(search_args) == 0:
                cur.execute(state + where_sentence + order_sentence)
            else:
                cur.execute(state + where_sentence + order_sentence, search_args)
            for row in cur.fetchall():
                factory.create(**row)

        return factory
