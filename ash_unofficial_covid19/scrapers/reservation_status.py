from typing import Optional

import pandas as pd
import tabula

from ash_unofficial_covid19.scrapers.downloader import DownloadedPDF
from ash_unofficial_covid19.scrapers.scraper import Scraper


class ScrapeReservationStatus(Scraper):
    """旭川市新型コロナワクチン接種医療機関予約受付状況の取得

    旭川市公式ホームページからダウンロードしたPDFファイルのデータから、
    旭川市の新型コロナワクチン接種医療機関予約受付状況データを抽出し、リストに変換する。

    Attributes:
        reservation_status_data (list of dict): 医療機関予約受付状況データ
            旭川市の新型コロナワクチン接種医療機関予約受付状況データを表す辞書のリスト

    """

    def __init__(self, pdf_url: str):
        """
        Args:
            pdf_url (str): PDFファイルのURL
                旭川市の予約受付状況PDFファイルのURL

        """
        Scraper.__init__(self)
        downloaded_pdf = DownloadedPDF(pdf_url)
        pdf_df = self._get_dataframe(downloaded_pdf)
        self.__lists = self._get_status_data(pdf_df)

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_dataframe(self, downloaded_pdf: DownloadedPDF) -> pd.DataFrame:
        """
        Args:
            downloaded_pdf (BytesIO): PDFファイルデータ
                ダウンロードしたPDFファイルのBytesIOデータを要素に持つオブジェクト

        Returns:
            table_data (obj:`pd.DataFrame`): 医療機関予約受付状況PDFデータ
                旭川市の新型コロナワクチン接種医療機関予約受付状況PDFデータから抽出した
                表データを、pandas DataFrameで返す

        """
        return tabula.read_pdf(
            downloaded_pdf.content,
            lattice=True,
            pages="all",
            pandas_options={"header": None},
        )

    def _get_status_data(self, pdf_df: list) -> list:
        """
        Args:
            pdf_df (list of :obj:`pd.DataFrame`): PDFファイルから抽出した表データ

        Returns:
            status_data (list of dict): 医療機関予約受付状況データ
                旭川市の新型コロナワクチン接種医療機関予約受付状況PDFデータから抽出した
                表データを、医療機関予約受付状況データ辞書のリストで返す

        """
        status_data = list()
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
                extracted_data = self._extract_status_data(row)
                if extracted_data:
                    status_data.append(extracted_data)

        return status_data

    def _extract_status_data(self, row: list) -> Optional[dict]:
        """PDFから抽出した表データ二次元配列から新型コロナウイルス陽性患者情報のみ抽出

        Args:
            row (list): PDFから抽出した表データの1行を表すリスト

        Returns:
            status_data (dict): 患者データの辞書
                引数のリストが新型コロナウイルス陽性患者情報なら辞書にして返す

        """
        status_data = dict()
        try:
            if len(row) < 7:
                return None

            row = list(map(lambda x: self.format_string(x), row))
            medical_institution_name = row[0].replace(" ", "").replace("　", "")
            if medical_institution_name == "" or medical_institution_name == "医療機関名":
                return None

            status_data = {
                "medical_institution_name": medical_institution_name,
                "address": row[1],
                "phone_number": row[2],
                "status": row[3],
                "target": row[4],
                "inoculation_time": row[5],
                "memo": row[6],
            }
        except IndexError:
            return None

        return status_data

    def get_name_list(self) -> list:
        """スクレイピング結果から主キーとなる医療機関名のリストを取得

        Returns:
            name_list (list): スクレイピングした医療機関名のリスト

        """
        name_list = list()
        for reservation_status in self.lists:
            name_list.append(reservation_status["medical_institution_name"])
        return name_list
