from datetime import datetime, timedelta, timezone

from psycopg2.extras import DictCursor

from ..models.location import LocationFactory
from ..services.service import Service


class LocationService(Service):
    """医療機関の緯度経度データを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "locations")

    def create(self, locations: LocationFactory) -> None:
        """データベースへ医療機関の緯度経度データを保存

        Args:
            locations (:obj:`LocationFactory`): 医療機関の緯度経度データ
                医療機関の緯度経度データのオブジェクトのリストを要素に持つオブジェクト

        """
        items = (
            "medical_institution_name",
            "longitude",
            "latitude",
            "updated_at",
        )

        data_lists = list()
        for location in locations.items:
            data_lists.append(
                [
                    location.medical_institution_name,
                    location.longitude,
                    location.latitude,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="medical_institution_name",
            data_lists=data_lists,
        )

    def find_all(self) -> LocationFactory:
        """医療機関の緯度経度データの全件リストを返す

        Returns:
            res (:obj:`LocationFactory`): 医療機関の緯度経度一覧データ
                医療機関の緯度経度データのオブジェクトのリストを要素に持つオブジェクト

        """
        state = (
            "SELECT"
            + " "
            + "medical_institution_name,longitude,latitude"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY id"
            + ";"
        )
        factory = LocationFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory
