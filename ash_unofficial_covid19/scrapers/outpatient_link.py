import re

from bs4 import BeautifulSoup

from ..config import Config
from ..scrapers.downloader import DownloadedHTML
from ..scrapers.scraper import Scraper


class ScrapeOutpatientLink(Scraper):
    """旭川市新型コロナウイルス発熱外来データExcelファイルのリンクの抽出

    北海道公式ホームページから旭川市の新型コロナウイルス発熱外来データExcelファイルの
    リンクを抽出する。

    Attributes:
        lists (list of dict): 旭川市の発熱外来データExcelファイルのURLを表す辞書のリスト

    """

    def __init__(self, html_url: str):
        """
        Args:
            html_url (str): HTMLファイルのURL
                北海道の発熱外来一覧一覧ページのURL

        """
        Scraper.__init__(self)
        self.__lists = list()
        self.__lists.append(self.get_source_excel_link(html_url))

    @property
    def lists(self) -> list:
        return self.__lists

    def get_source_excel_link(self, html_url: str) -> dict:
        """スクレイピングの元ExcelファイルのURLを抽出して返す

        Args:
            html_url (str): HTMLファイルのURL

        Returns:
            source_excel_link (str): 発熱外来一覧ExcelファイルのURL

        """
        source_excel_link = {
            "url": "",
        }
        downloaded_html = DownloadedHTML(html_url)
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        for article in soup.find_all("article"):
            # id属性などで対象を絞れないためdiv要素を全てなめる。
            # 子要素にa要素があればhref属性を取得し、それがExcelファイルへのリンクか判断。
            # 更にa要素の子要素にimg要素がありalt属性の値に「旭川」を含んでいればリンク文字列を取得。
            for div in soup.find_all("div"):
                a = div.find("a")
                if a:
                    href = a.get("href")
                    if href:
                        if re.match(r"^.*.xlsx$", href):
                            img = div.find("img")
                            if img:
                                alt = img.get("alt")
                                if alt:
                                    if re.match("^.*旭川.*$", alt):
                                        source_excel_link["url"] = Config.OUTPATIENTS_BASE_URL + href

        return source_excel_link
