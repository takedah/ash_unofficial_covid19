import urllib.parse
from dataclasses import dataclass, field

from ..models.factory import Factory


@dataclass()
class Area:
    """新型コロナワクチン接種医療機関の地区データモデル

    新型コロナワクチン接種医療機関の地区名称とこれをURLパースした文字列を要素に持つ
    データモデル。

    Attributes:
        name (str): 地区名称
        url (str): 地区をURLパースした文字列

    """

    name: str = ""
    url: str = field(init=False)

    def __post_init__(self):
        self.url = urllib.parse.quote(self.name)


class AreaFactory(Factory):
    """新型コロナワクチン接種医療機関の地区データオブジェクトを生成

    Attributes:
        items (list of :obj:`Area`): 医療機関の地区データリスト
            Areaクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> Area:
        """Areaオブジェクトの生成

        Args:
            row (dict): 医療機関の地区データの辞書
                新型コロナワクチン接種医療機関の地区データオブジェクトを
                作成するための引数

        Returns:
            item (:obj:`Area`): 医療機関の地区データ
                Areaクラスのオブジェクト

        """
        return Area(**row)

    def _register_item(self, item: Area):
        """Areaオブジェクトをリストへ追加

        Args:
            item (:obj:`Area`): データオブジェクト
                Areaクラスのオブジェクト

        """
        self.__items.append(item)
