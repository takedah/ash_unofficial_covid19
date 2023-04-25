import re
import urllib.parse

from bs4 import BeautifulSoup

from ..errors import ScrapeError
from ..scrapers.downloader import DownloadedHTML
from ..scrapers.scraper import Scraper


class ScrapePressReleaseLink(Scraper):
    """新型コロナウイルス感染症の市内発生状況ページの報道発表資料へのリンクを抽出

    Attributes:
        lists (list of dict): 報道発表日と報道発表PDFへのリンクリスト
            報道発表日と報道発表PDFへのリンクを要素とする辞書ののリスト

    """

    def __init__(self, html_url: str, target_year: int = 2020):
        """
        Args:
            html_url (str): HTMLファイルのURL
            target_year (int): 元データに年が表記されていないため直接指定する

        """
        if 2020 <= target_year:
            self.__target_year = target_year
        else:
            raise ScrapeError("対象年の指定が正しくありません。")

        Scraper.__init__(self)
        downloaded_html = DownloadedHTML(html_url)
        self.__lists = self._get_press_release_link(downloaded_html)

    @property
    def lists(self):
        return self.__lists

    @property
    def target_year(self) -> int:
        return self.__target_year

    def _get_press_release_link(self, downloaded_html: DownloadedHTML) -> list:
        """新型コロナウイルス感染症の発生状況の報道発表PDFへのリンクを抽出

        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードしたHTMLファイルのbytesデータを要素に持つオブジェクト

        Returns:
            press_release_link (list of dict): tableの内容で構成される二次元配列

        """
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        press_release_link = list()
        for a in soup.find_all("a"):
            anker_text = self.format_string(self.z2h_number(a.text.strip()))

            # 令和4年2月21日発表分のリンクテキストが誤っている部分対策
            if anker_text == "新型コロナウイルス感染症の発生状況（令和4年2月20日発表分）（PDF形式 58キロバイト）":
                values = {
                    "url": urllib.parse.urljoin(downloaded_html.url, a["href"]),
                    "publication_date": self.format_date("2月21日", 2022),
                }
                press_release_link.append(values)
                continue

            search_press_release = re.match("新型コロナウイルス感染症の発生状況.*([0-9]+月[0-9]+日)発表分.*", anker_text)
            if search_press_release is not None:
                public_date_string = search_press_release.group(1)
                values = {
                    "url": urllib.parse.urljoin(downloaded_html.url, a["href"]),
                    "publication_date": self.format_date(public_date_string, self.target_year),
                }
                press_release_link.append(values)

        return sorted(press_release_link, key=lambda x: x["publication_date"])
