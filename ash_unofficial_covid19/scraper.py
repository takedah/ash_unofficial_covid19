import csv
import re
from datetime import date, datetime
from io import BytesIO, StringIO
from typing import Optional

import pandas as pd
import requests
import tabula
from bs4 import BeautifulSoup
from requests import HTTPError, Timeout

from ash_unofficial_covid19.errors import HTTPDownloadError
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

    def _get_html_content(self, url: str) -> bytes:
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
            raise HTTPDownloadError(message)
        if response.status_code != 200:
            message = "cannot get HTML contents."
            self._error_log(message)
            raise HTTPDownloadError(message)
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
                        val = td.text.strip()
                        row.append(val)
                    row = list(
                        map(
                            lambda x: re.sub("( +)", " ", x)
                            .replace("\r", " ")
                            .replace("\n", " "),
                            row,
                        )
                    )
                    table_values.append(row)

        return table_values

    @staticmethod
    def _z2h(zenkaku_string: str) -> str:
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
            date_string = ScrapedHTMLData._z2h(
                date_string.replace(" ", "").replace("　", "")
            )
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
        age_string = ScrapedHTMLData._z2h(age_string)
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


class ScrapedCSVData:
    """北海道新型コロナウイルス感染症患者データの抽出

    北海道オープンデータポータルからダウンロードした陽性患者属性CSVファイルから、
    新型コロナウイルス感染症患者データを抽出し、リストに変換する。

    Attributes:
        patients_data (list of dict): 患者データを表す辞書のリスト

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): CSVファイルのURL

        """
        self.__logger = AppLog()
        self.__patients_data = list()
        csv_io = self._get_csv_io(url=url, encoding="cp932")
        for row in self._get_table_values(csv_io):
            extracted_data = self._extract_patient_data(row)
            if extracted_data is not None:
                self.__patients_data.append(extracted_data)

    @property
    def patients_data(self) -> list:
        return self.__patients_data

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

    def _get_csv_io(self, url: str, encoding: str = "utf-8") -> StringIO:
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
            self._info_log("CSVファイルのダウンロードに成功しました。")
        except (ConnectionError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self._error_log(message)
            raise HTTPDownloadError(message)
        if response.status_code != 200:
            message = "cannot get CSV contents."
            self._error_log(message)
            raise HTTPDownloadError(message)
        return csv_io

    def _get_table_values(self, csv_io: StringIO) -> list:
        """CSVから内容を抽出してリストに格納

        Args:
            csv_io (:obj:`StringIO`): ダウンロードしたCSVファイルのStringIOデータ

        Returns:
            table_values (list of list): CSVの内容で構成される二次元配列

        """
        table_values = list()
        reader = csv.reader(csv_io)
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


class DownloadedPDF:
    """旭川市新型コロナワクチン接種医療機関一覧PDFファイルのスクレイピング

    旭川市公式ホームページからダウンロードしたPDFファイルから、
    新型コロナワクチン接種医療機関一覧データをpandasのDataFrameで抽出する。

    Attributes:
        extraced_data (obj:`pd.DataFrame`): ワクチン接種医療機関一覧PDFから
            抽出したデータ

    """

    def __init__(self, pdf_url: str):
        """
        Args:
            pdf_url (str): PDFファイルのURL

        """
        self.__logger = AppLog()
        self.__extracted_data = self._get_pdf_content(pdf_url)

    @property
    def extracted_data(self) -> list:
        return self.__extracted_data

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

    def _get_pdf_content(self, pdf_url: str) -> pd.DataFrame:
        """
        Args:
            pdf_url (str): PDFファイルのURL

        Returns:
            pdf_content (obj:`pd.DataFrame`): ワクチン接種医療機関一覧PDFデータから
                抽出したデータ

        """
        try:
            # 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて回避する
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
            response = requests.get(pdf_url)
            self._info_log("PDFファイルのダウンロードに成功しました。")
        except (ConnectionError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self._error_log(message)
            raise HTTPDownloadError(message)

        if response.status_code != 200:
            message = "cannot get PDF contents."
            self._error_log(message)
            raise HTTPDownloadError(message)

        dfs = tabula.read_pdf(
            BytesIO(response.content), multiple_tables=True, lattice=True, pages="all"
        )
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


class ScrapedPDFData:
    """旭川市新型コロナワクチン接種医療機関一覧データの抽出

    旭川市公式ホームページからダウンロードしたPDFファイルのデータから、
    新型コロナワクチン接種医療機関一覧データを抽出し、リストに変換する。

    Attributes:
        medical_institution_data (list of dict): ワクチン接種医療機関データを表す
            辞書のリスト

    """

    def __init__(self, pdf_content: DownloadedPDF):
        """
        Args:
            pdf_content (obj:`DownloadedPDF`): PDFファイルのデータをpandasのDataFrameに
                抽出したデータを持つオブジェクト

        """
        self.__logger = AppLog()
        self.__medical_institutions_data = self.extract_from_pdf(pdf_content)

    @property
    def medical_institutions_data(self) -> list:
        return self.__medical_institutions_data

    def extract_from_pdf(self, pdf_content: DownloadedPDF) -> list:
        """
        Args:
            pdf_content (obj:`DownloadedPDF`): PDFファイルのデータをpandasのDataFrameに
                抽出したデータを持つオブジェクト

        Returns:
            pdf_data (list of dict): ワクチン接種医療機関データを表す辞書のリスト

        """
        df = pdf_content.extracted_data
        # 見出し行を削除し、最終行が注釈なのでこれも削除
        df.drop(df.index[[0, -1]], inplace=True)
        # 最終列がNaNのみの列なので削除
        df.drop(columns="null", inplace=True)
        df.replace("\r", "", regex=True, inplace=True)
        # 表が2段組なので左側の列のみを取り出す
        left_df = df[
            [
                "name1",
                "address1",
                "phone_number1",
                "book_at_medical_institution1",
                "book_at_call_center1",
            ]
        ]
        # 右側の列のみを取り出す
        right_df = df[
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


class ScrapedMedicalInstitutionsHTMLData:
    """旭川市新型コロナワクチン接種医療機関の一覧を抽出

    旭川市公式WebサイトからダウンロードしたHTMLファイルから、
    新型コロナワクチン接種医療機関データを抽出し、リストに変換する。

    Attributes:
        items (list of dict): 医療機関データを表す辞書のリスト

    """

    def __init__(self, downloaded_html: DownloadedHTML):
        """
        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードした旭川市公式サイトの
                新型コロナ接種医療機関のページのHTMLファイルのbytesデータ
                を要素に持つオブジェクト

        """
        self.__items = list()
        for row in self._get_table_values(downloaded_html):
            extracted_data = self._extract_medical_institutions_data(row)
            if extracted_data is not None:
                self.__items.append(extracted_data)

    @property
    def items(self) -> list:
        return self.__items

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
            if table_caption == "新型コロナワクチン接種医療機関一覧":
                area = ""
                for tr in table.find_all("tr"):
                    row = list()
                    th = tr.find("th")
                    if th:
                        area = th.text.strip().replace("\n", "")
                    row.append(area)
                    for td in tr.find_all("td"):
                        val = td.text.strip().replace("\n", "")
                        row.append(val)
                    row = list(
                        map(
                            lambda x: x.replace("\n", "")
                            .replace("\r", "")
                            .replace(" ", ""),
                            row,
                        )
                    )
                    table_values.append(row)

        return table_values

    def _extract_medical_institutions_data(self, row: list) -> Optional[dict]:
        """新型コロナワクチン接種医療機関データへの変換

        旭川市公式ホームページのワクチン接種医療機関一覧HTMLから抽出した行データの
        リストを、辞書に変換する。

        Args:
            row (list): table要素から抽出した行データのリスト

        Returns:
            medical_institutions_data (dict): 新型コロナワクチン接種医療機関データを
                表すハッシュ

        """
        try:
            if isinstance(row[2], str):
                address = "旭川市" + row[2]
            else:
                address = ""
            if isinstance(row[3], str):
                if row[3] == "":
                    phone_number = ""
                else:
                    phone_number = "0166-" + row[3]
            else:
                phone_number = ""
            if row[4] == "○":
                book_at_medical_institution = True
            else:
                book_at_medical_institution = False
            if row[5] == "○":
                book_at_call_center = True
            else:
                book_at_call_center = False
            medical_institutions_data = {
                "name": row[1],
                "address": address,
                "phone_number": phone_number,
                "book_at_medical_institution": book_at_medical_institution,
                "book_at_call_center": book_at_call_center,
                "area": row[0],
            }
            return medical_institutions_data
        except (ValueError, IndexError):
            return None
