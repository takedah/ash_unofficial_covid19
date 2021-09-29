import csv
from datetime import date, datetime
from typing import Optional

from ..scrapers.downloader import DownloadedCSV
from ..scrapers.scraper import Scraper


class ScrapeSapporoPatientsNumber(Scraper):
    """札幌市の新型コロナウイルス感染症日別患者数データの抽出

    DATA-SMART CITY SAPPOROからダウンロードした陽性患者数CSVファイルから、
    札幌市の新型コロナウイルス感染症日別患者数データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 患者数データを表す辞書のリスト

    """

    def __init__(self, csv_url: str):
        """
        Args:
            csv_url (str): CSVファイルのURL

        """
        Scraper.__init__(self)
        downloaded_csv = self.get_csv(csv_url=csv_url, encoding="utf-8")
        self.__lists = list()
        for row in self._get_table_values(downloaded_csv):
            extracted_data = self._extract_patients_number_data(row)
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
        next(reader)
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
        if not isinstance(date_string, str) or date_string == "":
            return None

        try:
            formatted_datetime = datetime.strptime(date_string, "%Y-%m-%d")
        except (TypeError, ValueError):
            return None

        return date(
            formatted_datetime.year, formatted_datetime.month, formatted_datetime.day
        )

    def _extract_patients_number_data(self, row: list) -> Optional[dict]:
        """札幌市の新型コロナウイルス感染症日別患者数データへの変換

        DATA-SMART CITY SAPPOROの陽性患者数CSVから抽出した行データのリストを
        ハッシュに変換する。

        Args:
            row (list): table要素から抽出した行データのリスト

        Returns:
            patients_number_data (dict): 札幌市の日別患者数データを表すハッシュ

        """
        try:
            date_string = row[0]
            if not isinstance(date_string, str):
                return None

            date_string = date_string[:10]
            patients_number_data = {
                "publication_date": self._format_date(date_string),
                "patients_number": int(row[1]),
            }
            return patients_number_data
        except (ValueError, IndexError):
            return None
