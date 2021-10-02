from ..services.patient import AsahikawaPatientService


class AsahikawaPatientsView:
    """旭川市新型コロナウイルス陽性患者データ

    旭川市新型コロナウイルス陽性患者データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = AsahikawaPatientService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self) -> str:
        return self.__last_updated

    def get_csv(self) -> str:
        """グラフのデータをCSVで返す

        Returns:
            csv_data (str): グラフのCSVデータ

        """
        return self.__service.get_csv()

    def get_rows(self, page: int = 1, desc: bool = True) -> tuple:
        """グラフのデータをオブジェクトデータのリストで返す

        ページネーションできるよう指定したページ番号分のデータのみ返す

        Args:
            page (int): ページ番号
            desc (bool): 真なら降順、偽なら昇順でリストを返す

        Returns:
            rows (tuple): ページネーションデータ
                AsahikawaPatientFactoryオブジェクトと
                ページネーションした場合の最大ページ数の数値を要素に持つタプル

        """
        return self.__service.find(page=page, desc=desc)
