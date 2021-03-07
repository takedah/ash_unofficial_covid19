import re
from datetime import date
from typing import Optional

import requests
from bs4 import BeautifulSoup
from requests import HTTPError, Timeout

from ash_unofficial_covid19.errors import HTMLDownloadError
from ash_unofficial_covid19.logs import AppLog


class DownloadedHTML:
    """HTMLファイルのbytesデータの取得

    WebサイトからHTMLファイルをダウンロードしてbytesデータに変換する。

    Attributes:
        content (bytes): ダウンロードしたHTMLファイルのbytesデータ

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): WebサイトのHTMLファイルのURL

        """
        self.__logger = AppLog()
        self.__content = self._get_html_content(url)

    @property
    def content(self) -> bytes:
        return self.__content

    def _info_log(self, message: str) -> None:
        """AppLog.infoのラッパー

        Args:
            message (str): 通常のログメッセージ

        """
        self.__logger.info(message)

    def _error_log(self, message: str) -> None:
        """AppLog.errorのラッパー

        Args:
            message (str): エラーログメッセージ

        """
        self.__logger.error(message)

    def _get_html_content(self, url) -> bytes:
        """WebサイトからHTMLファイルのbytesデータを取得

        Args:
            url (str): HTMLファイルのURL

        Returns:
            content (bytes): ダウンロードしたHTMLファイルのbytesデータ

        """
        try:
            # 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて回避する
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
            response = requests.get(url)
            self._info_log("HTMLファイルのダウンロードに成功しました。")
        except (ConnectionError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self._error_log(message)
            raise HTMLDownloadError(message)
        if response.status_code != 200:
            message = "cannot get HTML contents."
            self._error_log(message)
            raise HTMLDownloadError(message)
        return response.content


class ScrapedHTMLData:
    """旭川市新型コロナウイルス感染症患者データの抽出

    旭川市公式WebサイトからダウンロードしたHTMLファイルから、
    新型コロナウイルス感染症患者データを抽出し、リストに変換する。

    Attributes:
        patients_data (list of dict): 患者データを表す辞書のリスト
        target_year (int): 取得データの属する年

    """

    def __init__(self, downloaded_html: DownloadedHTML, target_year: int = 2020):
        """
        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードした旭川市公式サイトの
                新型コロナウイルス感染症の市内発生状況のページのHTMLファイルのbytesデータ
                を要素に持つオブジェクト
            target_year (int): 元データに年が表記されていないため直接指定する

        """
        if 2020 <= target_year:
            self.__target_year = target_year
        else:
            raise TypeError("対象年の指定が正しくありません。")
        self.__patients_data = list()
        for row in self._get_table_values(downloaded_html):
            extracted_data = self._extract_patient_data(row)
            if extracted_data is not None:
                self.__patients_data.append(extracted_data)

    @property
    def patients_data(self) -> list:
        return self.__patients_data

    @property
    def target_year(self) -> int:
        return self.__target_year

    def _get_table_values(self, downloaded_html: DownloadedHTML) -> list:
        """HTMLからtableの内容を抽出してリストに格納

        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLファイルの
                bytesデータを要素に持つオブジェクト

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
                        val = td.text.strip().replace("\n", " ")
                        row.append(val)
                    table_values.append(row)

        return table_values

    @staticmethod
    def format_date(date_string: str, target_year: int) -> Optional[date]:
        """元データに年のデータがないためこれを加えてdatetime.dateに変換

        Args:
            date_string (str): 元データの日付表記
            target_year (int): 対象年

        Returns:
            formatted_date (date): datetime.dateに変換した日付データ

        """
        try:
            matched_texts = re.match("([0-9]+)月([0-9]+)日", date_string)
            if matched_texts is None:
                return None
            month_and_day = matched_texts.groups()
            month = int(month_and_day[0])
            day = int(month_and_day[1])
            return date(target_year, month, day)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def format_age(age_string: str) -> str:
        """患者の年代表記をオープンデータ定義書の仕様に合わせる。

        Args:
            age_string (str): 元データの患者の年代表記

        Returns:
            formatted_age (str): 修正後の患者の年代表記

        """
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
            # 旭川市公式サイトにあるがオープンデータ定義書にない項目は半角スペース区切りで
            # 全て備考に入れる。
            note = (
                "北海道発表NO.:"
                + " "
                + row[1]
                + " "
                + "周囲の患者の発生:"
                + " "
                + row[6]
                + " "
                + "濃厚接触者の状況:"
                + " "
                + row[7]
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
            }
            return patient_data
        except (ValueError, IndexError):
            return None
