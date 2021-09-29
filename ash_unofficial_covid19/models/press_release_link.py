from datetime import date

from ..models.factory import Factory


class PressReleaseLink:
    """新型コロナウイルス感染症の発生状況の報道発表資料PDFファイル自体の情報

        旭川市公式ホームページの最新の新型コロナウイルス感染症の発生状況の
        報道発表資料PDFファイル自体の情報を表すデータモデル

    Attributes:
        url (str): 報道発表資料PDFファイルのURL
        publication_date (date): 報道発表資料の公開日

    """

    def __init__(
        self,
        url: str,
        publication_date: date,
    ):
        """
        Args:
            url (str): 報道発表資料PDFファイルのURL
            publication_date (date): 報道発表資料の公開日

        """
        self.__url = url
        self.__publication_date = publication_date

    @property
    def url(self) -> str:
        return self.__url

    @property
    def publication_date(self) -> date:
        return self.__publication_date


class PressReleaseLinkFactory(Factory):
    """報道発表資料PDFファイル自体の情報を表すデータモデルを生成

    Attributes:
        items (list of :obj:`PressReleaseLink`): 報道発表資料PDFファイル自体の情報一覧
            PressReleaseLinkクラスのオブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, **row) -> PressReleaseLink:
        """PressReleaseLinkオブジェクトの生成

        Args:
            row (dict): 報道発表資料PDFファイル自体の情報データの辞書
                報道発表資料PDFファイル自体の情報データオブジェクトを作成するための引数

        Returns:
            press_release_link (:obj:`PressReleaseLink`): 報道発表資料自体の情報データ
                PressReleaseLinkクラスのオブジェクト

        """
        return PressReleaseLink(**row)

    def _register_item(self, item: PressReleaseLink):
        """PressReleaseLinkオブジェクトをリストへ追加

        Args:
            item (:obj:`PressReleaseLink`): PressReleaseLinkクラスのオブジェクト

        """
        self.__items.append(item)
