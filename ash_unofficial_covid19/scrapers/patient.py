import csv
import re
from datetime import date, datetime
from typing import Optional

import pandas as pd
import tabula
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from ash_unofficial_covid19.scrapers.downloader import (
    DownloadedCSV,
    DownloadedHTML,
    DownloadedPDF
)
from ash_unofficial_covid19.scrapers.scraper import Scraper


class ScrapeAsahikawaPatients(Scraper):
    """旭川市新型コロナウイルス感染症患者データの抽出

    旭川市公式WebサイトからダウンロードしたHTMLファイルから、
    新型コロナウイルス感染症患者データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 患者データを表す辞書のリスト
        target_year (int): 取得データの属する年

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
            raise TypeError("対象年の指定が正しくありません。")

        Scraper.__init__(self)
        downloaded_html = self.get_html(html_url)
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


class ScrapeHokkaidoPatients(Scraper):
    """北海道新型コロナウイルス感染症患者データの抽出

    北海道オープンデータポータルからダウンロードした陽性患者属性CSVファイルから、
    新型コロナウイルス感染症患者データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 患者データを表す辞書のリスト

    """

    def __init__(self, csv_url: str):
        """
        Args:
            csv_url (str): CSVファイルのURL

        """
        Scraper.__init__(self)
        downloaded_csv = self.get_csv(csv_url=csv_url, encoding="cp932")
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


class ScrapeAsahikawaPatientsPDF(Scraper):
    """旭川市新型コロナウイルス陽性患者データの抽出

    旭川市公式ホームページからダウンロードしたPDFファイルのデータから、
    旭川市の新型コロナウイルス陽性患者データを抽出し、リストに変換する。

    Attributes:
        asahikawa_patients_data (list of dict): 旭川市の陽性患者データ
            旭川市の新型コロナウイルス陽性患者データを表す辞書のリスト

    """

    def __init__(self, pdf_url: str, publication_date: date):
        """
        Args:
            pdf_url (str): PDFファイルのURL
                旭川市の報道発表PDFファイルのURL
           publication_date (date): 報道発表日
                報道発表PDFデータに公表日がないため、引数で指定した日付をセット

        """
        Scraper.__init__(self)
        if isinstance(publication_date, date):
            self.__publication_date = publication_date
        else:
            raise TypeError("報道発表日の指定が正しくありません。")

        downloaded_pdf = DownloadedPDF(pdf_url)
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

    def _get_patients_data(self, pdf_df: list) -> list:
        """
        Args:
            pdf_df (list of :obj:`pd.DataFrame`): PDFファイルから抽出した表データ

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
            df.dropna(how="all", inplace=True)
            df.drop_duplicates(inplace=True)
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
        surrounding_status = str(row[8])
        close_contact = str(row[9])
        note = (
            "北海道発表No.;"
            + str(hokkaido_patient_number)
            + ";"
            + "周囲の患者の発生;"
            + surrounding_status
            + ";"
            + "濃厚接触者の状況;"
            + close_contact
            + ";"
        )
        patient_data = {
            "patient_number": patient_number,
            "city_code": "01241",
            "prefecture": "北海道",
            "city_name": "旭川市",
            "publication_date": self.publication_date - relativedelta(days=1),
            "onset_date": None,
            "residence": row[4],
            "age": self.format_age(row[5]),
            "sex": self.format_sex(row[6]),
            "occupation": None,
            "status": None,
            "symptom": None,
            "overseas_travel_history": None,
            "be_discharged": None,
            "note": note,
            "hokkaido_patient_number": hokkaido_patient_number,
            "surrounding_status": surrounding_status,
            "close_contact": close_contact,
        }
        return patient_data
