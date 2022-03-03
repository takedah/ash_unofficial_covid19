from dataclasses import dataclass

from ..errors import DataModelError
from ..models.factory import Factory


@dataclass()
class Point:
    """
    緯度と経度を要素に持つ地点情報を表す

    Attributes:
        latitude (float): 緯度（北緯）を表す小数
        longitude (float): 経度（東経）を表す小数

    """

    latitude: float = 0
    longitude: float = 0

    def __post_init__(self):
        if not isinstance(self.latitude, float) or not isinstance(self.longitude, float):
            raise DataModelError("緯度経度は数値で指定してください。")

        if self.latitude < -90 and 90 < self.latitude:
            raise DataModelError("緯度に指定できない値が設定されています。")

        if self.longitude < -180 and 180 < self.longitude:
            raise DataModelError("経度に指定できない値が設定されています。")


class PointFactory(Factory):
    """緯度経度を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`Point`): 緯度経度一覧リスト
            Pointクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> Point:
        """Pointオブジェクトの生成

        Args:
            row (dict): 緯度経度データの辞書
                緯度経度データオブジェクトを作成するための引数

        Returns:
            medical_institution (:obj:`Point`): 緯度経度データ
                Pointクラスのオブジェクト

        """
        return Point(**row)

    def _register_item(self, item: Point):
        """Pointオブジェクトをリストへ追加

        Args:
            item (:obj:`Point`): Pointクラスのオブジェクト

        """
        self.__items.append(item)
