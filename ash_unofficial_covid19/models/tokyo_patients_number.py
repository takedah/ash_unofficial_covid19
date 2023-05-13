from datetime import date

from ..models.factory import Factory


class TokyoPatientsNumber:
    """東京都の新型コロナウイルス感染症の日別新規患者数を表すモデルオブジェクト

    Attributes:
        publication_date (date): 公表日
        patients_number (int): 新規患者数

    """

    def __init__(self, publication_date: date, patients_number: int):
        """
        Args:
            publication_date (date): 公表日
            patients_number (int): 新規患者数

        """
        self.__publication_date = publication_date
        self.__patients_number = patients_number

    @property
    def publication_date(self):
        return self.__publication_date

    @property
    def patients_number(self):
        return self.__patients_number


class TokyoPatientsNumberFactory(Factory):
    """東京都の新型コロナウイルス感染症の日別新規患者数を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`TokyoPatientsNumber`): 東京都の日別新規患者数一覧リスト
            TokyoPatientsNumberクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self):
        return self.__items

    def _create_item(self, **row) -> TokyoPatientsNumber:
        """TokyoPatientsNumberオブジェクトの生成

        Args:
            row (dict): 東京都の日別新規患者数データの辞書
                東京都の新型コロナウイルス感染症日別新規患者数データオブジェクトを
                作成するための引数

        Returns:
            tokyo_patients_number (:obj:`TokyoPatientsNumber`): 日別新規患者数データ
                TokyoPatientsNumberクラスのオブジェクト

        """
        return TokyoPatientsNumber(**row)

    def _register_item(self, item: TokyoPatientsNumber):
        """TokyoPatientsNumberオブジェクトをリストへ追加

        Args:
            item (:obj:`TokyoPatientsNumber`): TokyoPatientsNumberクラスのオブジェクト

        """
        self.__items.append(item)
