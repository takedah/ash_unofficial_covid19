import csv
import re
import urllib.parse
from abc import ABCMeta, abstractmethod
from datetime import date, datetime
from io import BytesIO, StringIO
from json import JSONDecodeError
from typing import Optional

import pandas as pd
import requests
import tabula
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from flask import escape
from requests import HTTPError, Timeout

from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.errors import HTTPDownloadError
from ash_unofficial_covid19.logs import AppLog


class Downloader(metaclass=ABCMeta):
    """Webからコンテンツをダウンロードするクラスの基底クラス"""

    def __init__(self):
        self.__logger = AppLog()

    @property
    @abstractmethod
    def content(self):
        pass

    @property
    @abstractmethod
    def url(self):
        pass

    def info_log(self, message: str) -> None:
        """AppLog.infoのラッパー

        Args:
            message (str): 通常のログメッセージ

        """
        if isinstance(message, str):
            self.__logger.info(message)
        else:
            self.__logger.info("通常メッセージの指定が正しくない")

    def error_log(self, message: str) -> None:
        """AppLog.errorのラッパー

        Args:
            message (str): エラーログメッセージ

        """
        if isinstance(message, str):
            self.__logger.error(message)
        else:
            self.__logger.info("エラーメッセージの指定が正しくない")


class Scraper(metaclass=ABCMeta):
    """ダウンロードしたコンテンツを解析するクラスの基底クラス"""

    @property
    @abstractmethod
    def lists(self):
        pass

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
    def format_date(self, date_string: str, target_year: int) -> Optional[date]:
        """元データに年のデータがないためこれを加えてdatetime.dateに変換

        Args:
            date_string (str): 元データの日付表記
            target_year (int): 対象年

        Returns:
            formatted_date (date): datetime.dateに変換した日付データ

        """
        try:
            date_string = self.z2h_number(date_string.replace(" ", "").replace("　", ""))
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
    def format_age(self, age_string: str) -> str:
        """患者の年代表記をオープンデータ定義書の仕様に合わせる。

        Args:
            age_string (str): 元データの患者の年代表記

        Returns:
            formatted_age (str): 修正後の患者の年代表記

        """
        age_string = self.z2h_number(age_string)
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

    @classmethod
    def format_sex(self, sex_string: str) -> str:
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


class DownloadedHTML(Downloader):
    """HTMLファイルのbytesデータの取得

    WebサイトからHTMLファイルをダウンロードしてbytesデータに変換する。

    Attributes:
        content (bytes): ダウンロードしたHTMLファイルのbytesデータ
        url (str): HTMLファイルのURL

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): WebサイトのHTMLファイルのURL

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_html_content(self.__url)

    @property
    def content(self) -> bytes:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_html_content(self, url: str) -> bytes:
        """WebサイトからHTMLファイルのbytesデータを取得

        Args:
            url (str): HTMLファイルのURL

        Returns:
            content (bytes): ダウンロードしたHTMLファイルのbytesデータ

        """
        try:
            # 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて
            # 回避する
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
            response = requests.get(url)
            self.info_log("HTMLファイルのダウンロードに成功しました。")
        except (ConnectionError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)
        if response.status_code != 200:
            message = "cannot get HTML contents."
            self.error_log(message)
            raise HTTPDownloadError(message)
        return response.content


class ScrapeAsahikawaPatients(Scraper):
    """旭川市新型コロナウイルス感染症患者データの抽出

    旭川市公式WebサイトからダウンロードしたHTMLファイルから、
    新型コロナウイルス感染症患者データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 患者データを表す辞書のリスト
        target_year (int): 取得データの属する年

    """

    def __init__(self, downloaded_html: DownloadedHTML, target_year: int = 2020):
        """
        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードした旭川市公式サイトの新型コロナウイルス感染症の
                市内発生状況のページのHTMLファイルのbytesデータを要素に持つオブジェクト
            target_year (int): 元データに年が表記されていないため直接指定する

        """
        if 2020 <= target_year:
            self.__target_year = target_year
        else:
            raise TypeError("対象年の指定が正しくありません。")
        self.__lists = list()
        for row in self._get_table_values(downloaded_html):
            extracted_data = self._extract_patient_data(row)
            if extracted_data is not None:
                self.__lists.append(extracted_data)

    @property
    def lists(self) -> list:
        return self.__lists

    @property
    def target_year(self) -> int:
        return self.__target_year

    def _get_table_values(self, downloaded_html: DownloadedHTML) -> list:
        """HTMLからtableの内容を抽出してリストに格納

        Args:
            downloaded_html (obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードしたHTMLファイルのbytesデータを要素に持つオブジェクト

        Returns:
            table_values (list of list): tableの内容で構成される二次元配列

        """
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        table_values = list()
        for table in soup.find_all("table"):
            if table.find("caption") is not None:
                table_caption = table.find("caption").text.strip().replace("\n", "")
            else:
                table_caption = None
            if table_caption == "新型コロナウイルス感染症の市内発生状況":
                for tr in table.find_all("tr"):
                    row = list()
                    for td in tr.find_all("td"):
                        val = td.text.strip()
                        row.append(val)
                    row = list(map(lambda x: self.format_string(x), row))
                    table_values.append(row)

        return table_values

    def _extract_patient_data(self, row: list) -> Optional[dict]:
        """新型コロナウイルス感染症患者データへの変換

        新型コロナウイルス感染症の市内発生状況HTMLのtable要素から抽出した行データの
        リストを、Code for Japan (https://www.code4japan.org/activity/stopcovid19) の
        オープンデータ定義書に沿った新型コロナウイルス感染症患者データを表すハッシュに
        変換する。

        Args:
            row (list): table要素から抽出した行データのリスト

        Returns:
            patient_data (dict): 新型コロナウイルス感染症患者データを表すハッシュ

        """
        try:
            patient_number = int(row[0])
            hokkaido_patient_number = int(row[1])
            # 旭川市公式サイトにあるがオープンデータ定義書にない項目は半角スペース区切りで
            # 全て備考に入れる。
            note = (
                "北海道発表No."
                + ";"
                + row[1]
                + ";"
                + "周囲の患者の発生"
                + ";"
                + row[6]
                + ";"
                + "濃厚接触者の状況"
                + ";"
                + row[7]
                + ";"
            )
            patient_data = {
                "patient_number": patient_number,
                "city_code": "012041",  # 旭川市の総務省の全国地方公共団体コード
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": self.format_date(
                    date_string=row[2], target_year=self.target_year
                ),
                "onset_date": None,  # 元データにないため空とする
                "residence": row[5],
                "age": self.format_age(row[3]),
                "sex": self.format_sex(row[4]),
                "occupation": "",  # 元データにないため空とする
                "status": "",  # 元データにないため空とする
                "symptom": "",  # 元データにないため空とする
                "overseas_travel_history": None,  # 元データにないため空とする
                "be_discharged": None,  # 元データにないため空とする
                "note": note,
                "hokkaido_patient_number": hokkaido_patient_number,
                "surrounding_status": row[6],
                "close_contact": row[7],
            }
            return patient_data
        except (ValueError, IndexError):
            return None


class ScrapePressReleaseLink(Scraper):
    """新型コロナウイルス感染症の市内発生状況ページの報道発表資料へのリンクを抽出

    Attributes:
        lists (list of dict): 報道発表日と報道発表PDFへのリンクリスト
            報道発表日と報道発表PDFへのリンクを要素とする辞書ののリスト

    """

    def __init__(self, downloaded_html: DownloadedHTML, target_year: int = 2020):
        """
        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードした旭川市公式サイトの新型コロナウイルス感染症の
                市内発生状況のページのHTMLファイルのbytesデータを要素に持つオブジェクト
            target_year (int): 元データに年が表記されていないため直接指定する

        """
        if 2020 <= target_year:
            self.__target_year = target_year
        else:
            raise TypeError("対象年の指定が正しくありません。")

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
            press_release_link (list of tuple): tableの内容で構成される二次元配列

        """
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        press_release_link = list()
        for a in soup.find_all("a"):
            anker_text = self.format_string(self.z2h_number(a.text.strip()))
            search_press_release = re.match(
                "新型コロナウイルス感染症の発生状況.*令和[0-9]+年([0-9]+月[0-9]+日)発表分.*", anker_text
            )
            if search_press_release is not None:
                public_date_string = search_press_release.group(1)
                values = {
                    "url": urllib.parse.urljoin(downloaded_html.url, a["href"]),
                    "publication_date": self.format_date(
                        public_date_string, self.target_year
                    ),
                }
                press_release_link.append(values)

        return sorted(press_release_link)


class DownloadedCSV(Downloader):
    """CSVファイルのStringIOデータの取得

    WebサイトからCSVファイルをダウンロードしてStringIOで返す

    Attributes:
        content (StringIO): ダウンロードしたCSVファイルのStringIOデータ
        url (str): ダウンロードしたCSVファイルのURL

    """

    def __init__(self, url: str, encoding: str = "utf-8"):
        """
        Args:
            url (str): WebサイトのCSVファイルのURL
            encoding (str): CSVファイルの文字コード

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_csv_content(url=self.__url, encoding=encoding)

    @property
    def content(self) -> StringIO:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_csv_content(self, url: str, encoding: str) -> StringIO:
        """WebサイトからCSVファイルのStringIOデータを取得

        Args:
            url (str): CSVファイルのURL
            encoding (str): CSVファイルの文字コード

        Returns:
            content (:obj:`StringIO`): ダウンロードしたCSVファイルのStringIOデータ

        """
        try:
            response = requests.get(url)
            csv_io = StringIO(response.content.decode(encoding))
            self.info_log("CSVファイルのダウンロードに成功しました。")
        except (ConnectionError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)
        if response.status_code != 200:
            message = "cannot get CSV contents."
            self.error_log(message)
            raise HTTPDownloadError(message)
        return csv_io


class ScrapeHokkaidoPatients(Scraper):
    """北海道新型コロナウイルス感染症患者データの抽出

    北海道オープンデータポータルからダウンロードした陽性患者属性CSVファイルから、
    新型コロナウイルス感染症患者データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 患者データを表す辞書のリスト

    """

    def __init__(self, downloaded_csv: DownloadedCSV):
        """
        Args:
            downloaded_csv (:obj:`DownloadedCSV`):
            CSVファイルのStringIOデータを要素に持つオブジェクト

        """
        Scraper.__init__(self)
        self.__lists = list()
        for row in self._get_table_values(downloaded_csv):
            extracted_data = self._extract_patient_data(row)
            if extracted_data is not None:
                self.__lists.append(extracted_data)

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_table_values(self, downloaded_csv: DownloadedCSV) -> list:
        """CSVから内容を抽出してリストに格納

        Args:
            downloaded_csv (:obj:`DownloadedCSV`): CSVファイルのデータ
                ダウンロードしたCSVファイルのStringIOデータを要素に持つオブジェクト

        Returns:
            table_values (list of list): CSVの内容で構成される二次元配列

        """
        table_values = list()
        reader = csv.reader(downloaded_csv.content)
        for row in reader:
            table_values.append(row)

        return table_values

    @staticmethod
    def _format_date(date_string: str) -> Optional[date]:
        """文字列の日付をdatetime.dateに変換する

        Args:
            date_string (str): 日付文字列

        Returns:
            formatted_date (obj:`date`): 日付データ

        """
        try:
            if date_string == "":
                return None
            else:
                formatted_datetime = datetime.strptime(date_string, "%Y-%m-%d")
        except (TypeError, ValueError):
            return None

        return date(
            formatted_datetime.year, formatted_datetime.month, formatted_datetime.day
        )

    @staticmethod
    def _format_bool(bool_string: str) -> Optional[bool]:
        """文字列の真偽値をboolに変換する

        Args:
            date_string (str): 文字列真偽値

        Returns:
            formatted_bool (bool): 真偽値データ

        """
        try:
            if bool_string == "":
                return None
            elif bool_string == "0" or bool_string == "1":
                return bool(int(bool_string))
            else:
                return None
        except (TypeError, ValueError):
            return None

    def _extract_patient_data(self, row: list) -> Optional[dict]:
        """新型コロナウイルス感染症患者データへの変換

        北海道オープンデータポータルの陽性患者属性CSVから抽出した行データの
        リストを、Code for Japan (https://www.code4japan.org/activity/stopcovid19) の
        オープンデータ定義書に沿った新型コロナウイルス感染症患者データを表すハッシュに
        変換する。

        Args:
            row (list): table要素から抽出した行データのリスト

        Returns:
            patient_data (dict): 新型コロナウイルス感染症患者データを表すハッシュ

        """
        try:
            patient_number = int(row[0])
            patient_data = {
                "patient_number": patient_number,
                "city_code": row[1],
                "prefecture": row[2],
                "city_name": row[3],
                "publication_date": self._format_date(row[4]),
                "onset_date": self._format_date(row[5]),
                "residence": row[6],
                "age": row[7],
                "sex": row[8],
                "occupation": row[9],
                "status": row[10],
                "symptom": row[11],
                "overseas_travel_history": self._format_bool(row[12]),
                "be_discharged": self._format_bool(row[14]),
                "note": row[15],
            }
            return patient_data
        except (ValueError, IndexError):
            return None


class DownloadedPDF(Downloader):
    """PDFファイルのBytesIOデータの取得

    WebサイトからPDFファイルをダウンロードしてBytesIOで返す

    Attributes:
        content (BytesIO): ダウンロードしたPDFファイルのBytesIOデータ
        url (str): ダウンロードしたPDFファイルのURL

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): WebサイトのPDFファイルのURL

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_pdf_content(self.__url)

    @property
    def content(self) -> BytesIO:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_pdf_content(self, url: str) -> BytesIO:
        """WebサイトからCSVファイルのBytesIOデータを取得

        Args:
            url (str): PDFファイルのURL

        Returns:
            pdf_io (BytesIO): ワクチン接種医療機関一覧PDFデータから抽出したデータ

        """
        try:
            # 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて
            # 回避する
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
            response = requests.get(url)
            self.info_log("PDFファイルのダウンロードに成功しました。")
        except (ConnectionError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)

        if response.status_code != 200:
            message = "cannot get PDF contents."
            self.error_log(message)
            raise HTTPDownloadError(message)

        return BytesIO(response.content)


class ScrapeAsahikawaPatientsPDF(Scraper):
    """旭川市新型コロナウイルス陽性患者データの抽出

    旭川市公式ホームページからダウンロードしたPDFファイルのデータから、
    旭川市の新型コロナウイルス陽性患者データを抽出し、リストに変換する。

    Attributes:
        asahikawa_patients_data (list of dict): 旭川市の陽性患者データ
            旭川市の新型コロナウイルス陽性患者データを表す辞書のリスト

    """

    def __init__(self, downloaded_pdf: DownloadedPDF, publication_date: date):
        """
        Args:
            downloaded_pdf (:obj:`DownloadedPDF`): PDFデータ
                旭川市の報道発表PDFファイルのBytesIOデータを要素に持つオブジェクト
           publication_date (date): 報道発表日
                報道発表PDFデータに公表日がないため、引数で指定した日付をセット

        """
        if isinstance(publication_date, date):
            self.__publication_date = publication_date - relativedelta(days=1)
        else:
            raise TypeError("報道発表日の指定が正しくありません。")

        pdf_df = self._get_dataframe(downloaded_pdf)
        self.__lists = self._get_patients_data(pdf_df)

    @property
    def lists(self) -> list:
        return self.__lists

    @property
    def publication_date(self) -> date:
        return self.__publication_date

    def _get_dataframe(self, downloaded_pdf: DownloadedPDF) -> pd.DataFrame:
        """
        Args:
            downloaded_pdf (BytesIO): PDFファイルデータ
                ダウンロードしたPDFファイルのBytesIOデータを要素に持つオブジェクト

        Returns:
            table_data (obj:`pd.DataFrame`): 旭川市の新型コロナウイルス陽性患者PDFデータ
                旭川市の新型コロナウイルス陽性患者PDFデータから抽出した表データを、
                pandas DataFrameで返す

        """
        return tabula.read_pdf(downloaded_pdf.content, lattice=True, pages="all")

    def _get_patients_data(self, pdf_df: pd.DataFrame) -> list:
        """
        Args:
            pdf_io (obj:`pd.DataFrame`): PDFファイルから抽出した表データ

        Returns:
            patients_data (list of dict): 旭川市の新型コロナウイルス陽性患者PDFデータ
                旭川市の新型コロナウイルス陽性患者PDFデータから抽出した表データを、
                患者データ辞書のリストで返す

        """
        patients_data = list()
        for df in pdf_df:
            # データフレームが空の場合スキップ
            if df.empty:
                continue
            df.fillna("", inplace=True)
            pdf_table = df.values.tolist()
            header_row = pdf_table[0]
            # 見出し行かどうかまず要素数で判定
            if len(header_row) < 3:
                continue
            # 見出し行が決まった文字列の場合のみデータ抽出
            if header_row[1] == "市内番号" and header_row[2] == "道内番号":
                for row in pdf_table[1:]:
                    extracted_data = self._extract_patient_data(row)
                    if extracted_data:
                        patients_data.append(extracted_data)

        return patients_data

    def _extract_patient_data(self, row: list) -> Optional[dict]:
        """PDFから抽出した表データ二次元配列から新型コロナウイルス陽性患者情報のみ抽出

        Args:
            row (list): PDFから抽出した表データの1行を表すリスト

        Returns:
            patient_data (dict): 患者データの辞書
                引数のリストが新型コロナウイルス陽性患者情報なら辞書にして返す

        """
        search_patient_number = re.match("^([0-9]{,4})$", row[1].strip())
        search_hokkaido_patient_number = re.match("^([0-9]{,5})$", row[2].strip())
        if search_patient_number is None or search_hokkaido_patient_number is None:
            return None
        patient_number = int(search_patient_number.group(1))
        hokkaido_patient_number = int(search_hokkaido_patient_number.group(1))
        patient_data = {
            "patient_number": patient_number,
            "city_code": "01241",
            "prefecture": "北海道",
            "city_name": "旭川市",
            "publication_date": self.publication_date,
            "onset_date": None,
            "residence": row[4],
            "age": self.format_age(row[5]),
            "sex": self.format_sex(row[6]),
            "occupation": None,
            "status": None,
            "symptom": None,
            "overseas_travel_history": None,
            "be_discharged": None,
            "note": "北海道発表No.;" + str(hokkaido_patient_number),
            "hokkaido_patient_number": hokkaido_patient_number,
            "surrounding_status": None,
            "close_contact": None,
        }
        return patient_data


class ScrapeMedicalInstitutionsPDF(Scraper):
    """旭川市新型コロナワクチン接種医療機関一覧データの抽出

    旭川市公式ホームページからダウンロードしたPDFファイルのデータから、
    新型コロナワクチン接種医療機関一覧データを抽出し、リストに変換する。

    Attributes:
        medical_institution_data (list of dict): ワクチン接種医療機関データ
            ワクチン接種医療機関データを表す辞書のリスト

    """

    def __init__(self, downloaded_pdf: DownloadedPDF):
        """
        Args:
            downloaded_pdf (:obj:`DownloadedPDF`): PDFデータ
                PDFファイルのBytesIOデータを要素に持つオブジェクト

        """
        pdf_df = self._get_dataframe(downloaded_pdf.content)
        self.__lists = self._extract_medical_institutions_data(pdf_df)

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_dataframe(self, pdf_io: BytesIO) -> pd.DataFrame:
        """
        Args:
            pdf_io (BytesIO): PDFファイルのBytesIOデータ

        Returns:
            pdf_content (obj:`pd.DataFrame`): ワクチン接種医療機関一覧PDFデータ
                ワクチン接種医療機関一覧PDFデータから抽出したpandas DataFrameデータ

        """
        dfs = tabula.read_pdf(pdf_io, multiple_tables=True, lattice=True, pages="all")
        df = dfs[0]
        df.columns = [
            "name1",
            "address1",
            "phone_number1",
            "book_at_medical_institution1",
            "book_at_call_center1",
            "name2",
            "address2",
            "phone_number2",
            "book_at_medical_institution2",
            "book_at_call_center2",
            "null",
        ]
        return df

    def _extract_medical_institutions_data(self, pdf_df: pd.DataFrame) -> list:
        """
        Args:
            pdf_df (:obj:`pd.DataFrame`): PDFファイルから抽出したpandasのDataFrameデータ

        Returns:
            pdf_data (list of dict): ワクチン接種医療機関データを表す辞書のリスト

        """
        # 見出し行を削除し、最終行が注釈なのでこれも削除
        pdf_df.drop(pdf_df.index[[0, -1]], inplace=True)
        # 最終列がNaNのみの列なので削除
        pdf_df.drop(columns="null", inplace=True)
        pdf_df.replace("\r", "", regex=True, inplace=True)
        # 表が2段組なので左側の列のみを取り出す
        left_df = pdf_df[
            [
                "name1",
                "address1",
                "phone_number1",
                "book_at_medical_institution1",
                "book_at_call_center1",
            ]
        ]
        # 右側の列のみを取り出す
        right_df = pdf_df[
            [
                "name2",
                "address2",
                "phone_number2",
                "book_at_medical_institution2",
                "book_at_call_center2",
            ]
        ]
        left_df.columns = [
            "name",
            "address",
            "phone_number",
            "book_at_medical_institution",
            "book_at_call_center",
        ]
        right_df.columns = [
            "name",
            "address",
            "phone_number",
            "book_at_medical_institution",
            "book_at_call_center",
        ]
        formatted_df = pd.concat([left_df, right_df])
        # 後で行番号で更新するときのために行番号を振り直す
        formatted_df.reset_index(inplace=True, drop=True)

        # 地区名を追加する処理
        formatted_df["area"] = ""
        area = ""
        for index, row in formatted_df.iterrows():
            # 「かかりつけの医療機関で〜」、「コールセンターやインターネットで〜」列が
            # np.NaNの場合、地区名の見出しなので、文字列を抽出して地区データを追記する
            if row[3] == row[3] and row[4] == row[4]:
                formatted_df.at[index, "area"] = area
            else:
                cols = row.fillna("")
                area = cols[0] + cols[1] + cols[2]
                # 地区名が欠損しているので修正
                if area == "中央地":
                    area = "中央地区"
                elif area == "西地":
                    area = "西地区"
                elif area == "大成地":
                    area = "大成地区"
                elif area == "豊岡":
                    area = "豊岡"
                elif area == "東光・神":
                    area = "東光・旭神"
                elif area == "東旭":
                    area = "東旭川"
                elif area == "本・旭町・大町錦町・緑町":
                    area = "本町・旭町・大町・錦町・緑町"
                elif area == "各17~26丁・宮前・南":
                    area = "各条17~26丁目・宮前・南"
                elif area == "新富・東・星町":
                    area = "新富・東・金星町"
                elif area == "住吉・春光春光台":
                    area = "住吉・春光・春光台"
                elif area == "花町・末広・末東・東鷹栖":
                    area = "花咲町・末広・末広東・東鷹栖"
                elif area == "永山":
                    area = "永山"
                elif area == "神楽岡・が丘":
                    area = "神楽岡・緑が丘"
                elif area == "神居・和":
                    area = "神居・忠和"
                else:
                    area = ""
        # 元データから地区名の列を削除
        formatted_df.dropna(how="any", inplace=True)

        formatted_df["address"] = formatted_df["address"].apply(lambda x: "旭川市" + x)
        formatted_df["phone_number"] = formatted_df["phone_number"].apply(
            lambda x: "0166-" + x
        )
        formatted_df["book_at_medical_institution"] = formatted_df[
            "book_at_medical_institution"
        ].apply(lambda x: x == "○")
        formatted_df["book_at_call_center"] = formatted_df["book_at_call_center"].apply(
            lambda x: x == "○"
        )

        return formatted_df.to_dict(orient="records")


class ScrapeMedicalInstitutions(Scraper):
    """旭川市新型コロナワクチン接種医療機関の一覧を抽出

    旭川市公式WebサイトからダウンロードしたHTMLファイルから、
    新型コロナワクチン接種医療機関データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 医療機関データを表す辞書のリスト

    """

    def __init__(self, downloaded_html: DownloadedHTML):
        """
        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードした旭川市公式サイトの新型コロナ接種医療機関のページの
                HTMLファイルのbytesデータを要素に持つオブジェクト

        """
        self.__lists = list()
        table_values = self._get_table_values(downloaded_html)
        rows = table_values[0]
        memos = table_values[1]
        for row in rows:
            extracted_data = self._extract_medical_institution_data(
                row=row, memos=memos
            )
            if extracted_data is not None:
                self.__lists.append(extracted_data)

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_table_values(self, downloaded_html: DownloadedHTML) -> tuple:
        """HTMLからtableの内容を抽出してリストに格納

        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードしたHTMLファイルのbytesデータを要素に持つオブジェクト

        Returns:
            table_values (list of list): tableの内容で構成される二次元配列
            memos (dict): 備考欄の番号をキー、本文を値とした辞書

        """
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        table_values = list()
        for table in soup.find_all("table"):
            if table.find("caption") is not None:
                table_caption = table.find("caption").text.strip().replace("\n", "")
            else:
                table_caption = None
            if table_caption == "新型コロナワクチン接種医療機関一覧":
                area = ""
                memos = dict()
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

    def _extract_medical_institution_data(
        self, row: list, memos: dict
    ) -> Optional[dict]:
        """新型コロナワクチン接種医療機関データへの変換

        旭川市公式ホームページのワクチン接種医療機関一覧HTMLから抽出した行データの
        リストを、辞書に変換する。

        Args:
            row (list): table要素から抽出した行データのリスト
            memos (dict): 備考欄の番号をキー、本文を値とした辞書

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

            medical_institution_data = {
                "name": name,
                "address": address,
                "phone_number": phone_number,
                "book_at_medical_institution": book_at_medical_institution,
                "book_at_call_center": book_at_call_center,
                "area": row[0],
                "memo": memo,
            }
            return medical_institution_data
        except (ValueError, IndexError):
            return None


class DownloadedJSON(Downloader):
    """Web APIからJSONデータの取得

    WebサイトからJSONファイルをダウンロードして辞書データに変換する。

    Attributes:
        content (bytes): ダウンロードしたJSONファイルの辞書データ
        url (str): ダウンロードしたJSONファイルのURL

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): WebサイトのJSONファイルのURL

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_json_content(self.__url)

    @property
    def content(self) -> dict:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_json_content(self, url: str) -> dict:
        """WebサイトからJSONファイルの辞書データを取得

        Args:
            url (str): JSONファイルのURL

        Returns:
            content (dict): ダウンロードしたHTMLファイルのbytesデータ

        """
        try:
            response = requests.get(url)
            self.info_log("JSONファイルのダウンロードに成功しました。")
        except (ConnectionError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)

        if response.status_code != 200:
            message = "cannot get HTML contents."
            self.error_log(message)
            raise HTTPDownloadError(message)

        try:
            json_res = response.json()
        except JSONDecodeError:
            message = "cannot decode json response."
            self.error_log(message)
            raise HTTPDownloadError(message)

        return json_res


class ScrapeYOLPLocation(Scraper):
    """Yahoo! Open Local Platform (YOLP) Web APIから指定した施設の緯度経度情報を取得

    Attributes:
        lists (list of dict): 緯度経度データを表す辞書のリスト

    """

    def __init__(self, facility_name: str):
        """
        Args:
            facility_name (str): 緯度経度情報を取得したい施設の名称

        """
        self.__lists = list()
        if isinstance(facility_name, str):
            facility_name = urllib.parse.quote(escape(facility_name))
        else:
            raise TypeError("施設名の指定が正しくありません。")

        city_code = "01204"
        industry_code = "0401"
        if Config.YOLP_APP_ID:
            app_id = Config.YOLP_APP_ID
        else:
            raise RuntimeError("YOLPアプリケーションIDの指定が正しくありません。")

        json_url = (
            Config.YOLP_BASE_URL
            + "?appid="
            + app_id
            + "&query="
            + facility_name
            + "&ac="
            + city_code
            + "&gc="
            + industry_code
            + "&sort=-match&detail=simple&output=json"
        )
        downloaded_json = self._get_json(json_url)
        for search_result in self._get_search_results(downloaded_json):
            location_data = self._extract_location_data(search_result)
            location_data["medical_institution_name"] = urllib.parse.unquote(
                facility_name
            )
            self.__lists.append(location_data)

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_json(self, json_url: str) -> DownloadedJSON:
        """JSONデータを要素に持つオブジェクトを返す

        Args:
            json_url (str): YOLP Web APIのURL

        Returns:
            downloaded_json (:obj:`DownloadedJSON`): JSONデータを要素に持つオブジェクト

        """
        if isinstance(json_url, str):
            return DownloadedJSON(json_url)
        else:
            raise TypeError("Web API URLの指定が正しくありません。")

    def _get_search_results(self, downloaded_json: DownloadedJSON) -> list:
        """YOLP Web APIの返すJSONデータから検索結果データを抽出

        Args:
            downloaded_json (:obj:`DownloadedJSON`): JSONデータを要素に持つオブジェクト

        Returns:
            search_results (list of dict): 検索結果辞書データリスト
                JSONデータから検索結果の部分を辞書データで抽出したリスト

        """
        json_res = downloaded_json.content
        try:
            if json_res["ResultInfo"]["Count"] == 0:
                # 検索結果が0件の場合、緯度経度にダミーの値をセットして返す
                search_results = [
                    {
                        "Geometry": {
                            "Coordinates": "0,0",
                        },
                    },
                ]
            else:
                search_results = json_res["Feature"]
            return search_results
        except KeyError:
            raise RuntimeError("期待したJSONレスポンスが得られていません。")

    def _extract_location_data(self, search_result: dict) -> dict:
        """YOLP Web APIの返すJSONデータから緯度経度情報を抽出

        Args:
            yolp_json (dict): YOLP Web APIの返すJSONデータ

        Returns:
            location_data (dict): 緯度経度の辞書データ

        """
        location_data = dict()
        coordinates = search_result["Geometry"]["Coordinates"].split(",")
        location_data["longitude"] = float(coordinates[0])
        location_data["latitude"] = float(coordinates[1])
        return location_data
