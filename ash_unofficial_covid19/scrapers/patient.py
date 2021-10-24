import csv
import re
from datetime import date, datetime
from typing import Optional

import tabula
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta

from ..errors import ScrapeError
from ..scrapers.downloader import DownloadedCSV, DownloadedHTML, DownloadedPDF
from ..scrapers.scraper import Scraper


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
            raise ScrapeError("対象年の指定が正しくありません。")

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
        try:
            for table in soup.find_all("table"):
                for tr in table.find_all("tr"):
                    row = list()
                    for td in tr.find_all("td"):
                        val = td.text.strip()
                        row.append(val)
                    row = list(map(lambda x: self.format_string(x), row))
                    table_values.append(row)
        except AttributeError as e:
            raise ScrapeError(e.args[0])

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
            note = "北海道発表No." + ";" + row[1] + ";" + "周囲の患者の発生" + ";" + row[6] + ";" + "濃厚接触者の状況" + ";" + row[7] + ";"
            publication_date = self.format_date(date_string=row[2], target_year=self.target_year)
            # 旭川市公式ホームページの陽性患者データの日付は判明日（前日）のため、
            # 公表日に修正する。
            if publication_date:
                publication_date = publication_date + relativedelta(days=1)

            patient_data = {
                "patient_number": patient_number,
                "city_code": "012041",  # 旭川市の総務省の全国地方公共団体コード
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": publication_date,
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
        try:
            reader = csv.reader(downloaded_csv.content)
        except csv.Error as e:
            raise ScrapeError(e.args[0])

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

        return date(formatted_datetime.year, formatted_datetime.month, formatted_datetime.day)

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

    def _get_dataframe(self, downloaded_pdf: DownloadedPDF) -> list:
        """
        Args:
            downloaded_pdf (BytesIO): PDFファイルデータ
                ダウンロードしたPDFファイルのBytesIOデータを要素に持つオブジェクト

        Returns:
            table_data (list of obj:`pd.DataFrame`): 旭川市の新型コロナウイルス陽性患者PDFデータ
                旭川市の新型コロナウイルス陽性患者PDFデータから抽出した表データを、
                pandas DataFrameのリストで返す

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
            # リスト化した結果空リストだった場合スキップ
            if pdf_table == []:
                continue

            for row in pdf_table:
                if len(row) < 10:
                    continue
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
        try:
            search_patient_number = re.match("^([0-9]{,4})$", str(row[1]).strip())
            search_hokkaido_patient_number = re.match("^([0-9]{,5})$", str(row[2]).strip())
        except IndexError:
            return None

        if search_patient_number is None or search_hokkaido_patient_number is None:
            return None

        # 2021年8月のPDFに余計な列が入っている行があったので長さで判断して余計な要素を削除
        if len(row) == 11:
            row.pop(6)

        try:
            patient_number = int(search_patient_number.group(1))
            hokkaido_patient_number = int(search_hokkaido_patient_number.group(1))
        except ValueError:
            return None

        try:
            surrounding_status = self.format_string((row[8]))
            close_contact = self.format_string((row[9]))
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
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": self.publication_date,
                "onset_date": None,
                "residence": self.format_string(row[4]),
                "age": self.format_age(row[5]),
                "sex": self.format_sex(row[6]),
                "occupation": self.format_string(row[7]),
                "status": None,
                "symptom": None,
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": note,
                "hokkaido_patient_number": hokkaido_patient_number,
                "surrounding_status": surrounding_status,
                "close_contact": close_contact,
            }
        except IndexError:
            return None

        return patient_data
