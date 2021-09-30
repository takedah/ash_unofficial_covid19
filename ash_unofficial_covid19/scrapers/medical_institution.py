import re
from typing import Optional

from bs4 import BeautifulSoup

from ..scrapers.downloader import DownloadedHTML
from ..scrapers.scraper import Scraper


class ScrapeMedicalInstitutions(Scraper):
    """旭川市新型コロナワクチン接種医療機関の一覧を抽出

    旭川市公式WebサイトからダウンロードしたHTMLファイルから、
    新型コロナワクチン接種医療機関データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 医療機関データを表す辞書のリスト

    """

    def __init__(self, html_url: str, is_pediatric: bool = False):
        """
        Args:
            html_url (str): HTMLファイルのURL
            is_pediatric (bool): 12歳から15歳までの接種医療機関の場合真を指定

        """
        downloaded_html = self.get_html(html_url)
        self.__lists = list()
        if is_pediatric:
            table_values = self._get_pediatric_table_values(downloaded_html)
        else:
            table_values = self._get_table_values(downloaded_html)

        rows = table_values[0]
        memos = table_values[1]
        for row in rows:
            extracted_data = self._extract_medical_institution_data(row=row, memos=memos, is_pediatric=is_pediatric)
            if extracted_data is not None:
                self.__lists.append(extracted_data)

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_table_values(self, downloaded_html: DownloadedHTML) -> tuple:
        """HTMLから16歳以上の医療機関tableの内容を抽出してリストに格納

        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードしたHTMLファイルのbytesデータを要素に持つオブジェクト

        Returns:
            table_values (list of list): tableの内容で構成される二次元配列
            memos (dict): 備考欄の番号をキー、本文を値とした辞書

        """
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        table_values = list()
        memos = dict()
        for table in soup.find_all("table"):
            if table.find("caption") is not None:
                table_caption = table.find("caption").text.strip().replace("\n", "")
            else:
                table_caption = None
            if table_caption == "新型コロナワクチン接種医療機関":
                area = ""
                for tr in table.find_all("tr"):
                    row = list()
                    th = tr.find("th")
                    # th要素は地区か備考を表しているので、備考の場合番号と内容を辞書に
                    # 格納しておく
                    if th:
                        th_text = self.format_string(th.text)
                        match = re.match("^(※[0-9]+)(.+)$", th_text)
                        if match:
                            memo_number = match[1]
                            memo_body = match[2].strip()
                            memos[memo_number] = memo_body
                        else:
                            area = th_text
                        continue
                    row.append(area)
                    for td in tr.find_all("td"):
                        val = td.text
                        row.append(val)
                    row = list(map(lambda x: self.format_string(x), row))
                    table_values.append(row)

        return table_values, memos

    def _get_memo(self, value: str, memos: dict):
        """解析したHTMLから備考を抽出する

        Args:
            value (str): 備考を含む可能性のあるテキスト
            memos (dict): 備考欄の番号をキー、本文を値とした辞書

        Returns:
            memo (str): 抽出した備考テキスト

        """
        memo_match = re.match("^.*(※[0-9]).*$", value)
        if memo_match:
            memo_number = memo_match[1]
            memo = memos[memo_number]
        else:
            other_match = re.match("^.*○(.+)$", value)
            if other_match:
                memo = other_match[1]
            else:
                memo = ""
        return memo

    def _get_pediatric_table_values(self, downloaded_html: DownloadedHTML) -> tuple:
        """HTMLから12歳から15歳までの医療機関tableの内容を抽出してリストに格納

        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードしたHTMLファイルのbytesデータを要素に持つオブジェクト

        Returns:
            table_values (list of list): tableの内容で構成される二次元配列
            memos (dict): 備考欄の番号をキー、本文を値とした辞書

        """
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        table_values = list()
        memos = dict()  # 現在備考はないが今後備考が追加された時用に一応残す
        for table in soup.find_all("table"):
            if table.find("caption") is not None:
                table_caption = table.find("caption").text.strip().replace("\n", "")
            else:
                table_caption = None
            if table_caption == "新型コロナワクチン接種医療機関（12歳から15歳）":
                area = ""
                for tr in table.find_all("tr"):
                    row = list()
                    # 16歳以上のtableと違い、地区名の行にth要素が使われていない。
                    # 地区名の行はa要素にid属性でアンカーにしているので、これを取得。
                    if tr.td.find(id=True) is not None:
                        th = tr.find("td")
                    else:
                        th = None
                    if th:
                        th_text = self.format_string(th.text)
                        area = th_text
                        continue
                    row.append(area)

                    for td in tr.find_all("td"):
                        val = td.text
                        row.append(val)

                    # 16歳以上のtableと違い、表の見出し行にth要素が使われていない。
                    # テキストの値で見出し行か判断する。
                    if row[1] == "医療機関名":
                        continue
                    row = list(map(lambda x: self.format_string(x), row))
                    table_values.append(row)

        return table_values, memos

    def _extract_medical_institution_data(self, row: list, memos: dict, is_pediatric: bool = False) -> Optional[dict]:
        """新型コロナワクチン接種医療機関データへの変換

        旭川市公式ホームページのワクチン接種医療機関一覧HTMLから抽出した行データの
        リストを、辞書に変換する。

        Args:
            row (list): table要素から抽出した行データのリスト
            memos (dict): 備考欄の番号をキー、本文を値とした辞書
            is_pediatric (bool): 12歳から15歳までの接種医療機関の場合真を指定

        Returns:
            medical_institution_data (dict): 新型コロナワクチン接種医療機関データ
                新型コロナワクチン接種医療機関データを表すハッシュ

        """
        try:
            name = ""
            if isinstance(row[1], str):
                name = row[1].replace(" ", "").replace("　", "")

            address = ""
            if isinstance(row[2], str):
                address = "旭川市" + row[2]

            phone_number = ""
            if isinstance(row[3], str):
                phone_number = row[3].replace("‐", "-")
                if re.match("^[0-9]{2}-[0-9]{4}.*$", phone_number):
                    phone_number = "0166-" + phone_number

            memo = ""
            book_at_medical_institution = False
            if isinstance(row[4], str):
                match = re.match("^.*○.*$", row[4])
                if match:
                    book_at_medical_institution = True
                    memo = self._get_memo(value=row[4], memos=memos)

            book_at_call_center = False
            if isinstance(row[5], str):
                match = re.match("^.*○.*$", row[5])
                if match:
                    book_at_call_center = True
                    memo = self._get_memo(value=row[5], memos=memos)

            target_age = "16歳以上"
            if is_pediatric:
                target_age = "12歳から15歳まで"

            medical_institution_data = {
                "name": name,
                "address": address,
                "phone_number": phone_number,
                "book_at_medical_institution": book_at_medical_institution,
                "book_at_call_center": book_at_call_center,
                "area": row[0],
                "memo": memo,
                "target_age": target_age,
            }
            return medical_institution_data
        except (ValueError, IndexError):
            return None

    def get_name_lists(self) -> list:
        """スクレイピング結果から主キーとなる医療機関名と対象年齢のタプルのリストを取得

        Returns:
            name_list (list of tuple): スクレイピングした医療機関名と対象年齢のタプルのリスト

        """
        name_lists = list()
        for medical_institution in self.lists:
            name_lists.append((medical_institution["name"], medical_institution["target_age"]))
        return name_lists
