from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import TypedDict, Union

import numpy as np
from psycopg2.extras import DictCursor

from ..models.child_reservation_status import ChildReservationStatusLocationFactory
from ..models.first_reservation_status import FirstReservationStatusLocationFactory
from ..models.location import LocationFactory
from ..models.point import Point
from ..models.reservation_status import ReservationStatusLocation, ReservationStatusLocationFactory
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
            + "ORDER BY longitude,latitude"
            + ";"
        )
        factory = LocationFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory

    @staticmethod
    def get_distance(start_point: Point, end_point: Point) -> float:
        """
        2点間の距離を計算して返す。

        Args:
            start_point (obj:`Point`): 緯度と経度を要素に持つオブジェクト
            end_point (obj:`Point`): 緯度と経度を要素に持つオブジェクト

        Returns:
            distance (float): 2点間の距離（メートル、小数点以下第4位を切り上げ）

        """
        earth_radius = 6378137.00
        start_latitude = np.radians(start_point.latitude)
        start_longitude = np.radians(start_point.longitude)
        end_latitude = np.radians(end_point.latitude)
        end_longitude = np.radians(end_point.longitude)
        distance = earth_radius * np.arccos(
            np.sin(start_latitude) * np.sin(end_latitude)
            + np.cos(start_latitude) * np.cos(end_latitude) * np.cos(end_longitude - start_longitude)
        )
        return float(Decimal(str(distance)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))

    @classmethod
    def get_near_locations(
        self,
        locations: Union[
            ReservationStatusLocationFactory,
            FirstReservationStatusLocationFactory,
            ChildReservationStatusLocationFactory,
        ],
        current_point: Point,
    ) -> list:
        """
        現在地から直線距離で最も近い医療機関データのリストを返す。

        Args:
            locations (obj:`ReservationStatusLocationFactory`): 医療機関一覧データ
                緯度経度を持つ医療機関予約受付状況データオブジェクトのリストを要素に持つオブジェクト
            current_point (obj:`Point`): 現在地の緯度経度情報を持つオブジェクト

        Returns:
            near_locations (list of dicts): 現在地から最も近い上位5件の
                医療機関オブジェクトと順位、現在地までの距離（キロメートルに換算し
                小数点第3位を切り上げ）を要素に持つ辞書のリスト

        """
        tmp_locations = list()
        OrderedLocation = TypedDict(
            "OrderedLocation", {"order": int, "location": ReservationStatusLocation, "distance": float}
        )
        for location in locations.items:
            ordered_location: OrderedLocation = {
                "order": 0,
                "location": location,
                "distance": self.get_distance(start_point=current_point, end_point=location),
            }
            tmp_locations.append(ordered_location)

        near_locations = sorted(tmp_locations, key=lambda x: x["distance"])[:5]
        for i in range(len(near_locations)):
            # 現在地から近い順で連番を付与する。
            near_locations[i]["order"] = i + 1
            # 距離を分かりやすくするためキロメートルに変換する。
            near_locations[i]["distance"] = float(
                Decimal(str(near_locations[i]["distance"] / 1000)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            )

        return near_locations
