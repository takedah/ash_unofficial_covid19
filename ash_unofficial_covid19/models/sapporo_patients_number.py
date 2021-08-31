from datetime import date

from ash_unofficial_covid19.models.factory import Factory


class SapporoPatientsNumber:
    """札幌市の新型コロナウイルス感染症の日別新規患者数を表すモデルオブジェクト

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
    def publication_date(self) -> date:
        return self.__publication_date

    @property
    def patients_number(self) -> float:
        return self.__patients_number


class SapporoPatientsNumberFactory(Factory):
    """札幌市の新型コロナウイルス感染症の日別新規患者数を表すモデルオブジェクトを生成

    Attributes:
        items (list of :obj:`SapporoPatientsNumber`): 札幌市の日別新規患者数一覧リスト
            SapporoPatientsNumberクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, **row) -> SapporoPatientsNumber:
        """SapporoPatientsNumberオブジェクトの生成

        Args:
            row (dict): 札幌市の日別新規患者数データの辞書
                札幌市の新型コロナウイルス感染症日別新規患者数データオブジェクトを
                作成するための引数

        Returns:
            sapporo_patients_number (:obj:`SapporoPatientsNumber`): 医療機関データ
                SapporoPatientsNumberクラスのオブジェクト

        """
        return SapporoPatientsNumber(**row)

    def _register_item(self, item: SapporoPatientsNumber):
        """SapporoPatientsNumberオブジェクトをリストへ追加

        Args:
            item (:obj:`SapporoPatientsNumber`): SapporoPatientsNumberクラスのオブジェクト

        """
        self.__items.append(item)
