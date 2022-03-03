from decimal import ROUND_HALF_UP, Decimal

import numpy as np

from ..models.point import Point


class PointService:
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
