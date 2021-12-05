from psycopg2.extras import DictCursor

from ..errors import ServiceError
from ..models.reservation_status_location import ReservationStatusLocation, ReservationStatusLocationFactory
from ..services.service import Service


class ReservationStatusLocationService(Service):
    """旭川市新型コロナ接種医療機関予約受付状況に位置情報を付けたデータを扱うサービス"""

    def __init__(self, is_third_time: bool = False):
        """
        Args:
            is_third_time (bool): 3回目接種の医療機関の情報を取得する場合真を指定

        """
        if is_third_time:
            table_name = "reservation3_statuses"
        else:
            table_name = "reservation_statuses"

        Service.__init__(self, table_name)

    def upsert(self):
        pass

    def find(self, medical_institution_name: str) -> ReservationStatusLocation:
        """新型コロナワクチン接種医療機関の個別情報

        指定した新型コロナワクチン接種医療機関の情報を返す

        Args:
            medical_institution_name (str): 医療機関の名称

        Returns:
            results (:obj:`ReservationStatusLocation`): 医療機関データ
                新型コロナワクチン接種医療機関予約受付状況の情報に緯度経度を含めた
                データオブジェクト

        """
        state = (
            "SELECT "
            + "reserve.medical_institution_name,"
            + "address,phone_number,status,inoculation_time,"
            + "target_age,target_family,target_not_family,target_suberbs,target_other,"
            + "latitude,longitude,memo "
            + "FROM "
            + self.table_name
            + " "
            + "AS reserve "
            + "LEFT JOIN locations AS loc ON reserve.medical_institution_name="
            + "loc.medical_institution_name "
            + "WHERE reserve.medical_institution_name=%s;"
        )
        factory = ReservationStatusLocationFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (medical_institution_name,))
                res = cur.fetchone()

        if res is None:
            raise ServiceError("指定した名称の医療機関はありませんでした。")

        return factory.create(**dict(res))

    def find_all(self) -> ReservationStatusLocationFactory:
        """新型コロナワクチン接種医療機関予約受付状況全件を返す

        Args:
            medical_institution_name (str): 医療機関の名称

        Returns:
            results (:obj:`ReservationStatusLocationFactory`): 医療機関データ
                新型コロナワクチン接種医療機関予約受付状況の情報に緯度経度を含めた
                データのリストを要素に持つオブジェクト

        """
        state = (
            "SELECT "
            + "reserve.medical_institution_name,"
            + "address,phone_number,status,inoculation_time,"
            + "target_age,target_family,target_not_family,target_suberbs,target_other,"
            + "latitude,longitude,memo "
            + "FROM "
            + self.table_name
            + " "
            + "AS reserve "
            + "LEFT JOIN locations AS loc ON reserve.medical_institution_name="
            + "loc.medical_institution_name "
            + "ORDER BY address;"
        )
        factory = ReservationStatusLocationFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory
