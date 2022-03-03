from dataclasses import dataclass

from ..models.factory import Factory
from ..models.point import Point


@dataclass
class Location(Point):
    """医療機関の緯度経度を表すモデルオブジェクト

    Attributes:
        medical_institution_name (str): 医療機関の名称
        longitude (float): 医療機関のある経度
        latitude (float): 医療機関のある緯度

    """

    medical_institution_name: str = ""


class LocationFactory(Factory):
    """医療機関の緯度経度を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`Location`): 医療機関の緯度経度一覧リスト
            Locationクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> Location:
        """Locationオブジェクトの生成

        Args:
            row (dict): 医療機関の緯度経度データの辞書
                医療機関の緯度経度データオブジェクトを作成するための引数

        Returns:
            medical_institution (:obj:`Location`): 医療機関データ
                Locationクラスのオブジェクト

        """
        return Location(**row)

    def _register_item(self, item: Location):
        """Locationオブジェクトをリストへ追加

        Args:
            item (:obj:`Location`): Locationクラスのオブジェクト

        """
        self.__items.append(item)
