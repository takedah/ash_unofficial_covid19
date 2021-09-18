from typing import Optional

from psycopg2.extras import DictCursor

from ash_unofficial_covid19.models.medical_institution_location import (
    MedicalInstitutionLocationFactory
)
from ash_unofficial_covid19.services.service import Service


class MedicalInstitutionLocationService(Service):
    """旭川市新型コロナ接種医療機関に位置情報を付けたデータを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "medical_institutions")

    def find(self, area: Optional[str] = None, is_pediatric: bool = False) -> list:
        """新型コロナワクチン接種医療機関の位置情報一覧

        指定した対象年齢の新型コロナワクチン接種医療機関の一覧に医療機関の位置情報を
        付けて返す

        Args:
            area (str): 医療機関の地区
            target_age (str): 対象年齢が16歳以上または12歳から15歳までのいずれか

        Returns:
            locations (list of tuple): 位置情報付き医療機関一覧データ
                新型コロナワクチン接種医療機関の情報に緯度経度を含めたタプルのリスト

        """
        state = (
            "SELECT "
            + "name,address,phone_number,book_at_medical_institution,"
            + "book_at_call_center,area,memo,target_age,latitude,longitude "
            + "FROM "
            + self.table_name
            + " "
            + "LEFT JOIN locations ON "
            + self.table_name
            + ".name = locations.medical_institution_name "
            + "WHERE "
            + self.table_name
            + ".target_age=%s"
        )
        if is_pediatric:
            target_age = "12歳から15歳まで"
        else:
            target_age = "16歳以上"

        if area:
            state = state + " " + "AND area=%s"

        state = state + " " + "ORDER BY " + self.table_name + ".id;"
        factory = MedicalInstitutionLocationFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                if area:
                    cur.execute(state, (target_age, area))
                else:
                    cur.execute(state, (target_age,))
                for row in cur.fetchall():
                    medical_institution_location = dict(row)
                    factory.create(**medical_institution_location)
        return factory
