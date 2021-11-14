from ..models.patient import AsahikawaPatientFactory
from ..services.patient import AsahikawaPatientService
from ..views.view import View


class AsahikawaPatientView(View):
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
    def last_updated(self):
        return self.__last_updated

    def get_csv(self) -> str:
        """陽性患者属性CSVファイルの文字列データを返す

        Returns:
            csv_data (str): 陽性患者属性CSVファイルの文字列データ

        """
        csv_data = self.__service.get_rows()
        csv_data.insert(
            0,
            [
                "No",
                "全国地方公共団体コード",
                "都道府県名",
                "市区町村名",
                "公表_年月日",
                "発症_年月日",
                "患者_居住地",
                "患者_年代",
                "患者_性別",
                "患者_職業",
                "患者_状態",
                "患者_症状",
                "患者_渡航歴の有無フラグ",
                "患者_退院済フラグ",
                "備考",
            ],
        )
        return self.list_to_csv(csv_data)

    def find(self, page: int = 1, desc: bool = True) -> tuple[AsahikawaPatientFactory, int]:
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
