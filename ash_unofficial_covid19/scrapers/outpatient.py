import re
import unicodedata
from typing import Union

import numpy as np
import pandas as pd

from ..scrapers.scraper import Scraper


class ScrapeOutpatient(Scraper):
    """旭川市新型コロナウイルス発熱外来データの抽出

    北海道公式ホームページからダウンロードしたExcelファイルのデータから、
    旭川市の新型コロナウイルス発熱外来データを抽出し、リストに変換する。

    Attributes:
        outpatient_data (list of dict): 旭川市の発熱外来データ
            旭川市の新型コロナウイルス発熱外来データを表す辞書のリスト

    """

    def __init__(self, excel_url: str):
        """
        Args:
            excel_url (str): ExcelファイルのURL
                北海道のExcelファイルのURL

        """
        Scraper.__init__(self)
        excel_lists = self._get_excel_lists(excel_url)
        self.__lists = list()
        for excel_row in excel_lists:
            if excel_row:
                self.__lists.append(self._get_outpatient(excel_row))

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_excel_lists(self, excel_url: str) -> list:
        """
        Args:
            excel_url (str): ExcelファイルのURL
                北海道の発熱外来一覧表ExcelファイルのURL

        Returns:
            excel_lists (list of list): 北海道の発熱外来Excelデータ
                北海道の新型コロナウイルス発熱外来一覧表Excelデータから抽出した表データを、
                二次元配列のリストで返す。

        """
        excel_file = self.get_excel(excel_url)
        df = pd.read_excel(
            excel_file.content,
            sheet_name="Sheet1",
            header=None,
            index_col=None,
            skiprows=[0, 1, 2, 3],
            dtype=str,
        )
        df.replace(np.nan, "", inplace=True)
        return df.values.tolist()

    def _get_outpatient(self, excel_row: list) -> dict:
        """
        Args:
            row (list): Excelファイルから抽出した行データ
                北海道の発熱外来一覧表Excelファイルから行を抽出してリストにしたデータ

        Returns:
            outpatient_data (dict): 新型コロナウイルス陽性患者数Excelデータ
                旭川市の新型コロナウイルス陽性患者報道発表Excelデータから抽出した
                年代別陽性患者数データを辞書で返す。

        """
        if excel_row is None:
            return None

        excel_row = list(map(lambda x: self._normalize(x), excel_row))
        outpatient: dict[str, Union[str, bool]] = dict()
        is_target_family = False
        if excel_row[7] == "かかりつけ患者以外の診療も可":
            is_target_family = True

        is_positive_patients = self._get_available(excel_row[1])
        is_face_to_face_for_positive_patients = False
        is_online_for_positive_patients = False
        is_home_visitation_for_positive_patients = False
        if is_positive_patients:
            is_face_to_face_for_positive_patients = self._get_available(excel_row[51])
            is_online_for_positive_patients = self._get_available(excel_row[52])
            is_home_visitation_for_positive_patients = self._get_available(excel_row[53])

        outpatient = {
            "is_outpatient": self._get_available(excel_row[0]),
            "is_positive_patients": is_positive_patients,
            "public_health_care_center": excel_row[2],
            "medical_institution_name": excel_row[3],
            "city": excel_row[4],
            "address": excel_row[5],
            "phone_number": excel_row[6],
            "is_target_family": is_target_family,
            "is_pediatrics": self._get_available(excel_row[8]),
            "mon": self._get_opening_hours(excel_row[9:15]),
            "tue": self._get_opening_hours(excel_row[15:21]),
            "wed": self._get_opening_hours(excel_row[21:27]),
            "thu": self._get_opening_hours(excel_row[27:33]),
            "fri": self._get_opening_hours(excel_row[33:39]),
            "sat": self._get_opening_hours(excel_row[39:45]),
            "sun": self._get_opening_hours(excel_row[45:51]),
            "is_face_to_face_for_positive_patients": is_face_to_face_for_positive_patients,
            "is_online_for_positive_patients": is_online_for_positive_patients,
            "is_home_visitation_for_positive_patients": is_home_visitation_for_positive_patients,
            "memo": excel_row[57],
        }
        return outpatient

    def _normalize(self, text: str) -> str:
        """文字列から余計な空白等を取り除き、全角数字等を正規化して返す。

        Args:
            text (str): 正規化したい文字列

        Returns:
            nomalized_text (str): 正規化後の文字列

        """
        if not isinstance(text, str):
            return ""

        if text == "0":
            return ""

        return unicodedata.normalize("NFKC", self.format_string(text))

    @staticmethod
    def _get_available(text: str) -> bool:
        """文字列がマルなら真を、そうでなければ偽を返す。

        Args:
            text (str): 判定したい文字列

        Returns:
            result (bool): 文字列がマルなら真を、そうでなければ偽

        """
        result = False
        ok_match = re.search("^(.*)[○|〇](.*)$", text)
        if ok_match:
            result = True

        return result

    def _get_opening_hours(self, target_list: list) -> str:
        """診療時間を表すリストを結合して文字列で返す

        Args:
            target_list (list): Excelから抽出した診療時間を表す文字列のリスト

        Returns:
            opening_hours (str): リストが診療時間を表していたら文字列を結合して返す

        """
        am = ""
        pm = ""
        am_start = self._strip_if_time_format(target_list[0])
        am_end = self._strip_if_time_format(target_list[2])
        pm_start = self._strip_if_time_format(target_list[3])
        pm_end = self._strip_if_time_format(target_list[5])
        if am_start != "00:00" or am_end != "00:00":
            am = am_start + "～" + am_end

        if pm_start != "00:00" or pm_end != "00:00":
            pm = pm_start + "～" + pm_end

        if am == "":
            return pm
        else:
            if pm == "":
                return am
            else:
                return (am + "、" + pm).replace("～00:00、00:00～", "～")

    @staticmethod
    def _strip_if_time_format(target_text: str) -> str:
        """文字列がExcelの時刻表記文字列なら整形し、そうでないならそのまま文字列を返す

        Args:
            text (str): 判定したい文字列

        Returns:
            stripped_text (str):
                Excelの時刻表記文字列なら秒の部分を削除し、そうでないならそのまま文字列を返す

        """
        if not isinstance(target_text, str):
            return None

        time_format_match = re.search("^([0-9]{2}):([0-9]{2}):([0-9]{2})$", target_text)
        if time_format_match:
            return time_format_match.group(1) + ":" + time_format_match.group(2)
        else:
            return target_text

    def get_medical_institution_list(self) -> list:
        """スクレイピング結果から主キーとなる医療機関名のリストを取得

        Returns:
            medical_institution_list (list): 医療機関名のリスト
                スクレイピングした医療機関名をリストで返す。

        """
        medical_institution_list = list()
        for outpatient in self.lists:
            medical_institution_list.append(outpatient["medical_institution_name"])

        return medical_institution_list
