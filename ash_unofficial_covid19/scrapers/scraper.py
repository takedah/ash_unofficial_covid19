import re
from abc import ABCMeta, abstractmethod
from datetime import date
from typing import Optional

from ash_unofficial_covid19.scrapers.downloader import (
    DownloadedCSV,
    DownloadedHTML,
    DownloadedPDF
)


class Scraper(metaclass=ABCMeta):
    """ダウンロードしたコンテンツを解析するクラスの基底クラス"""

    @property
    @abstractmethod
    def lists(self):
        pass

    @staticmethod
    def get_html(html_url: str) -> DownloadedHTML:
        """HTMLファイルのbytesデータを要素に持つオブジェクトを返す

        Args:
            html_url (str): HTMLファイルのURL

        """
        return DownloadedHTML(html_url)

    @staticmethod
    def get_csv(csv_url: str, encoding: str = "utf-8") -> DownloadedCSV:
        """CSVファイルのbytesデータを要素に持つオブジェクトを返す

        Args:
            csv_url (str): CSVファイルのURL
            encoding (str): CSVファイルの文字コード

        """
        return DownloadedCSV(url=csv_url, encoding=encoding)

    @staticmethod
    def get_pdf(pdf_url: str) -> DownloadedPDF:
        """PDFファイルのBytesIOデータを要素に持つオブジェクトを返す

        Args:
            pdf_url (url): PDFファイルのURL

        """
        return DownloadedPDF(pdf_url)

    @staticmethod
    def format_string(value: str) -> str:
        """改行を半角スペースに置換し、文字列から連続する半角スペースを除去する

        Args:
            value (str): 整形前の文字列

        Returns:
            formatted_str (str): 整形後の文字列

        """
        if isinstance(value, str):
            return re.sub(
                "( +)", " ", value.replace("\r", " ").replace("\n", " ").strip()
            )
        else:
            return ""

    @staticmethod
    def z2h_number(zenkaku_string: str) -> str:
        """全角数字が含まれている文字列の全角数字を全て半角数字に変換する

        Args:
            zenkaku_string (str): 全角数字が含まれている文字列

        """
        z2h_table = str.maketrans(
            {
                "０": "0",
                "１": "1",
                "２": "2",
                "３": "3",
                "４": "4",
                "５": "5",
                "６": "6",
                "７": "7",
                "８": "8",
                "９": "9",
            }
        )
        if type(zenkaku_string) is str:
            return zenkaku_string.translate(z2h_table)
        else:
            return ""

    @classmethod
    def format_date(cls, date_string: str, target_year: int) -> Optional[date]:
        """元データに年のデータがないためこれを加えてdatetime.dateに変換

        Args:
            date_string (str): 元データの日付表記
            target_year (int): 対象年

        Returns:
            formatted_date (date): datetime.dateに変換した日付データ

        """
        try:
            date_string = cls.z2h_number(date_string.replace(" ", "").replace("　", ""))
            matched_texts = re.match("([0-9]+)月([0-9]+)日", date_string)
            if matched_texts is None:
                return None
            month_and_day = matched_texts.groups()
            month = int(month_and_day[0])
            day = int(month_and_day[1])
            return date(target_year, month, day)
        except (TypeError, ValueError):
            return None

    @classmethod
    def format_age(cls, age_string: str) -> str:
        """患者の年代表記をオープンデータ定義書の仕様に合わせる。

        Args:
            age_string (str): 元データの患者の年代表記

        Returns:
            formatted_age (str): 修正後の患者の年代表記

        """
        age_string = cls.z2h_number(age_string)
        if age_string is None:
            return ""
        if age_string == "非公表" or age_string == "調査中":
            return ""
        elif age_string == "10代未満" or age_string == "10歳未満":
            return "10歳未満"
        elif age_string == "90代":
            return "90歳以上"

        matched_text = re.match("([0-9]+)", age_string)
        if matched_text is None:
            return ""
        age = int(matched_text.group(1))
        if 90 < age:
            return "90歳以上"
        else:
            return str(age) + "代"

    @staticmethod
    def format_sex(sex_string: str) -> str:
        """患者の性別表記をオープンデータ定義書の仕様に合わせる。

        Args:
            sex_string (str): 元データの患者の性別表記

        Returns:
            formatted_sex (str): 修正後の患者の性別表記

        """
        if sex_string == "非公表" or sex_string == "調査中":
            return ""
        if sex_string == "その他":
            return "その他"
        matched_text = re.match("(男|女)", sex_string)
        if matched_text is None:
            return ""
        sex = matched_text.group(1)
        return sex + "性"
