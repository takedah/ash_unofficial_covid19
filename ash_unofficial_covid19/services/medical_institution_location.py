from typing import Optional

from psycopg2.extras import DictCursor

from ..errors import ServiceError
from ..models.medical_institution_location import MedicalInstitutionLocation, MedicalInstitutionLocationFactory
from ..services.service import Service


class MedicalInstitutionLocationService(Service):
    """旭川市新型コロナ接種医療機関に位置情報を付けたデータを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "medical_institutions")

    def upsert(self):
        pass

    def find(self, name: str, is_pediatric: bool = False) -> MedicalInstitutionLocation:
        """新型コロナワクチン接種医療機関の個別情報

        指定した新型コロナワクチン接種医療機関の情報を返す

        Args:
            name (str): 医療機関の名称
            target_age (bool): 対象年齢フラグ
                真の場合は対象年齢が12歳から15歳まで、偽の場合16歳以上を表す

        Returns:
            results (:obj:`MedicalInstitutionLocation`): 位置情報付き医療機関一覧データ
                新型コロナワクチン接種医療機関の情報に緯度経度を含めたデータオブジェクト

        """
        state = (
            "SELECT "
            + "name,address,phone_number,book_at_medical_institution,"
            + "book_at_call_center,area,memo,target_age,latitude,longitude "
            + "FROM "
            + self.table_name
            + " "
            + "AS med LEFT JOIN locations ON med.name = "
            + "locations.medical_institution_name "
            + "WHERE med.name=%s AND "
        )
        if is_pediatric:
            target_age = "12歳から15歳まで"
        else:
            target_age = "16歳以上"
        state = state + "med.target_age=%s;"

        factory = MedicalInstitutionLocationFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state, (name, target_age))
                res = cur.fetchone()

        if res is None:
            raise ServiceError("指定した名称の医療機関はありませんでした。")

        return factory.create(**dict(res))

    def find_area(self, area: Optional[str] = None, is_pediatric: bool = False) -> MedicalInstitutionLocationFactory:
        """新型コロナワクチン接種医療機関の位置情報一覧

        指定した対象年齢の新型コロナワクチン接種医療機関の一覧に医療機関の位置情報を
        付けて返す

        Args:
            area (str): 医療機関の地区
            target_age (bool): 対象年齢フラグ
                真の場合は対象年齢が12歳から15歳まで、偽の場合16歳以上を表す

        Returns:
            results (:obj:`MedicalInstitutionLocationFactory`): 位置情報付き医療機関一覧データ
                新型コロナワクチン接種医療機関の情報に緯度経度を含めたタプルのリスト

        """
        state = (
            "SELECT "
            + "name,address,phone_number,book_at_medical_institution,"
            + "book_at_call_center,area,memo,target_age,latitude,longitude "
            + "FROM "
            + self.table_name
            + " "
            + "AS med LEFT JOIN locations ON med.name = "
            + "locations.medical_institution_name WHERE med.target_age=%s"
        )
        if is_pediatric:
            target_age = "12歳から15歳まで"
        else:
            target_age = "16歳以上"

        if area:
            state = state + " " + "AND area=%s"

        state = state + " " + "ORDER BY med.area,med.address;"
        factory = MedicalInstitutionLocationFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                if area:
                    cur.execute(state, (target_age, area))
                else:
                    cur.execute(state, (target_age,))
                res = cur.fetchall()
                if cur.rownumber == 0:
                    raise ServiceError("指定した地域の医療機関はありませんでした。")
                for row in res:
                    factory.create(**dict(row))
        return factory
