import dataclasses
from datetime import date

from ..models.factory import Factory


@dataclasses.dataclass(frozen=True)
class PatientsNumber:
    """新型コロナウイルス感染症日別年代別陽性患者数を表すデータモデル

    Attributes:
        publication_date (datetime.date): 報道発表年月日
        age_under_10 (int): 10歳未満の患者数
        age_10s (int): 10代の患者数
        age_20s (int): 20代の患者数
        age_30s (int): 30代の患者数
        age_40s (int): 40代の患者数
        age_50s (int): 50代の患者数
        age_60s (int): 60代の患者数
        age_70s (int): 70代の患者数
        age_80s (int): 80代の患者数
        age_over_90 (int): 90歳以上の患者数
        investigating (int): 調査中等の患者数

    """

    publication_date: date
    age_under_10: int = 0
    age_10s: int = 0
    age_20s: int = 0
    age_30s: int = 0
    age_40s: int = 0
    age_50s: int = 0
    age_60s: int = 0
    age_70s: int = 0
    age_80s: int = 0
    age_over_90: int = 0
    investigating: int = 0


class PatientsNumberFactory(Factory):
    """新型コロナウイルス感染症日別年代別陽性患者数データモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`PatientsNumber`): 日別年代別陽性患者数データリスト
            PatientsNumberクラスのオブジェクトのリスト。

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> PatientsNumber:
        """PatientsNumberオブジェクトの生成

        Args:
            row (dict): 日別年代別陽性患者数データを表す辞書
                新型コロナウイルス感染症日別年代別患者数データオブジェクトを
                作成するための引数。

        Returns:
            patients_number (:obj:`PatientsNumber`): PatientsNumberクラスのオブジェクト

        """
        return PatientsNumber(**row)

    def _register_item(self, item: PatientsNumber):
        """PatientsNumberオブジェクトをリストへ追加

        Args:
            item (:obj:`PatientsNumber`): PatientsNumberクラスのオブジェクト

        """
        self.__items.append(item)
