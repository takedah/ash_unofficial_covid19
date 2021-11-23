import re
from typing import Optional

import tabula

from ..scrapers.downloader import DownloadedPDF
from ..scrapers.scraper import Scraper


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

    def _get_dataframe(self, downloaded_pdf: DownloadedPDF) -> list:
        """
        Args:
            downloaded_pdf (BytesIO): PDFファイルデータ
                ダウンロードしたPDFファイルのBytesIOデータを要素に持つオブジェクト

        Returns:
            table_data (list of obj:`pd.DataFrame`): 医療機関予約受付状況PDFデータ
                旭川市の新型コロナワクチン接種医療機関予約受付状況PDFデータから抽出した
                表データを、pandas DataFrameのリストで返す

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
        """PDFから抽出した表データ二次元配列から新型コロナワクチン接種医療機関の予約受付状況情報のみ抽出

        Args:
            row (list): PDFから抽出した表データの1行を表すリスト

        Returns:
            status_data (dict): 予約受付状況データの辞書
                引数のリストが予約受付状況情報なら辞書にして返す

        """
        status_data = dict()
        try:
            if len(row) < 9:
                return None

            if not isinstance(row[0], str):
                return None

            # 一つの列に医療機関名、住所、電話番号が改行で区切られてまとめられてしまっているため分解する
            tmp = row[0].split("\r")
            tmp_length = len(tmp)
            if tmp_length < 3:
                return None

            phone_number = tmp[-1]
            address = tmp[-2]
            i = 0
            medical_institution_name = ""
            while i < tmp_length - 2:
                medical_institution_name += tmp[i]
                i += 1

            row = list(map(lambda x: self.format_string(x), row))

            # 対象者の詳細を結合する
            target = row[3].replace("―", "")
            if target:
                target = "年齢" + target

            target_detail = ""
            family = self._get_available(row[4])
            if family["available"]:
                target_detail += "かかりつけの方" + family["text"]

            not_family = self._get_available(row[5])
            if not_family["available"]:
                if target_detail:
                    target_detail += "、"

                target_detail += "かかりつけ以外の方" + family["text"]

            if target_detail:
                if target:
                    target_detail = "で" + target_detail

            if row[6].replace("―", ""):
                target_detail = target_detail + "（" + row[6].replace("―", "") + "）"

            target += target_detail
            target = target

            medical_institution_name = medical_institution_name.replace(" ", "").replace("　", "")
            if (
                medical_institution_name == ""
                or medical_institution_name == "医療機関名"
                or medical_institution_name == "電話番号"
            ):
                return None

            status_data = {
                "medical_institution_name": self._translate_name(medical_institution_name),
                "address": address,
                "phone_number": phone_number,
                "status": row[1].replace("―", ""),
                "target": target,
                "inoculation_time": row[2].replace("―", ""),
                "memo": row[8],
            }
            return {k: v.replace("　", "") for k, v in status_data.items()}
        except IndexError:
            return None

    @staticmethod
    def _get_available(target_string: str) -> dict:
        """かかりつけ、かかりつけ以外の文字列から対象なのかどうかを判定し、付記があればその文字列を取得

        Args:
            target_string (str): ○を含む可能性のある文字列

        Returns:
            result (dict): ○が含まれてたらavailableキーに真をセット、textキーに付記文字列があればセット

        """
        if not isinstance(target_string, str):
            return {"available": False, "text": ""}

        family_match = re.search("^(.*)○(.*)$", target_string)
        family_text = ""
        if family_match:
            family_text = family_match.group(1) + family_match.group(2)
            return {"available": True, "text": family_text}
        else:
            return {"available": False, "text": ""}

    @staticmethod
    def _translate_name(medical_institution_name: str) -> str:
        """
        医療機関名の表記揺れをHTMLページの方の名称に揃える

        Args:
            medical_institution_name (str): 医療機関名

        Returns:
            translated_name (str): 変換後の医療機関名
                変換対象ではない医療機関名を指定した場合はそのまま変換せず返す

        """
        if not isinstance(medical_institution_name, str):
            return ""

        translate_table = {
            "くさのこどもクリニック": "小児科くさのこどもクリニック",
        }
        return translate_table.get(medical_institution_name, medical_institution_name)

    def get_name_list(self) -> list:
        """スクレイピング結果から主キーとなる医療機関名のリストを取得

        Returns:
            name_list (list): スクレイピングした医療機関名のリスト

        """
        name_list = list()
        for reservation_status in self.lists:
            name_list.append(reservation_status["medical_institution_name"])
        return name_list
