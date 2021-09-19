from psycopg2.extras import DictCursor

from ash_unofficial_covid19.errors import ServiceError
from ash_unofficial_covid19.models.medical_institution_location_reservation_status import (
    MedicalInstitutionLocationReservationStatus,
    MedicalInstitutionLocationReservationStatusFactory
)
from ash_unofficial_covid19.services.service import Service


class MedicalInstitutionLocationReservationStatusService(Service):
    """旭川市新型コロナ接種医療機関に位置情報と予約受付状況を付けたデータを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "reservation_statuses")

    def find(
        self, name: str, is_pediatric: bool = False
    ) -> MedicalInstitutionLocationReservationStatus:
        """新型コロナワクチン接種医療機関の個別情報

        指定した新型コロナワクチン接種医療機関の情報を返す

        Args:
            name (str): 医療機関の名称
            target_age (bool): 対象年齢フラグ
                真の場合は対象年齢が12歳から15歳まで、偽の場合16歳以上を表す

        Returns:
            results (:obj:`MedicalInstitutionLocationReservationStatus`): 医療機関データ
                新型コロナワクチン接種医療機関の情報に緯度経度と予約受付状況を含めた
                データオブジェクト

        """
        state = (
            "SELECT "
            + "name,med.address,med.phone_number,book_at_medical_institution,"
            + "book_at_call_center,area,med.memo,target_age,latitude,longitude,"
            + "status,reserve.target AS target_person,inoculation_time,reserve.memo "
            + "AS reservation_status_memo "
            + "FROM medical_institutions AS med LEFT JOIN locations AS loc ON med.name="
            + "loc.medical_institution_name "
            + "LEFT JOIN "
            + self.table_name
            + " "
            + "AS reserve ON med.name=reserve.medical_institution_name "
            + "WHERE med.name=%s AND "
        )
        if is_pediatric:
            target_age = "12歳から15歳まで"
        else:
            target_age = "16歳以上"
        state = state + "med.target_age=%s "
        factory = MedicalInstitutionLocationReservationStatusFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (name, target_age))
                res = cur.fetchone()
                if res is None:
                    raise ServiceError("指定した名称の医療機関はありませんでした。")
                return factory.create(**dict(res))
