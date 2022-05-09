import re
from typing import Optional

from bs4 import BeautifulSoup

from ..scrapers.downloader import DownloadedHTML
from ..scrapers.scraper import Scraper


class ScrapeReservationStatus(Scraper):
    """旭川市新型コロナワクチン接種医療機関予約受付状況の取得

    旭川市新型コロナワクチン接種特設サイトからダウンロードしたHTMLファイルのデータから、
    新型コロナワクチン接種医療機関予約受付状況データを抽出し、リストに変換する。

    Attributes:
        lists (list of dict): 医療機関予約受付状況データ
            新型コロナワクチン接種医療機関予約受付状況データを表す辞書のリスト

    """

    def __init__(self, html_url: str):
        """
        Args:
            html_url (str): HTMLファイルのURL
                新型コロナワクチン接種医療機関予約受付状況HTMLファイルのURL

        """
        Scraper.__init__(self)
        self.__lists = list()
        downloaded_html = self.get_html(html_url)
        table_data = self.get_table_data(downloaded_html, "tablepress-9-no-2")
        for row in table_data:
            extracted_data = self._extract_status_data(row)
            if extracted_data:
                self.__lists.append(extracted_data)

    @property
    def lists(self) -> list:
        return self.__lists

    def get_table_data(self, downloaded_html: DownloadedHTML, table_id: str) -> list:
        """HTMLから医療機関予約受付状況のtableの内容を抽出してリストに格納

        Args:
            downloaded_html (:obj:`DownloadedHTML`): ダウンロードしたHTMLデータ
                ダウンロードしたHTMLファイルのbytesデータを要素に持つオブジェクト
            table_id (str): 抽出対象のtable要素のid属性

        Returns:
            status_data (list of list): table要素の行列データ
                HTMLデータから抽出した表データを二次元配列リストで返す。

        """
        soup = BeautifulSoup(downloaded_html.content, "html.parser")
        table = soup.find("table", id=table_id)
        for tbody in table.find_all("tbody"):
            target_tbody = tbody

        status_data = list()
        for tr in target_tbody.find_all("tr"):
            row = list()
            for td in tr.find_all("td"):
                # 一つの列に医療機関名、住所、電話番号が改行で区切られて
                # まとめられてしまっているため分解する。
                if td.has_attr("class"):
                    if "column-2" in td.get("class"):
                        key_col = td.get_text(",", strip=True).split(",")
                        # 分割した要素数が少ない場合、空文字列で埋める。
                        if len(key_col) < 3:
                            i = 0
                            while i < 3 - len(key_col):
                                key_col.append("")
                                i += 1
                        # 分割した要素数が多い場合、先頭の要素を結合して切り詰める。
                        elif 3 < len(key_col):
                            tmp_phone_number = key_col[-1]
                            tmp_address = key_col[-2]
                            i = 0
                            tmp_medical_institution_name = ""
                            while i < len(key_col) - 2:
                                if tmp_medical_institution_name == "":
                                    tmp_medical_institution_name = key_col[i]
                                else:
                                    tmp_medical_institution_name += " " + key_col[i]
                                i += 1
                            key_col = [tmp_medical_institution_name, tmp_address, tmp_phone_number]
                        row.extend(key_col)
                    else:
                        row.append(td.get_text(" ", strip=True))
                else:
                    row.append(td.get_text(" ", strip=True))

            status_data.append(row)

        return status_data

    def _extract_status_data(self, row: list) -> Optional[dict]:
        """HTMLから抽出した行データ配列から予約受付状況情報を抽出

        Args:
            row (list): PDFから抽出した表データの1行を表すリスト

        Returns:
            status_data (dict): 予約受付状況データの辞書
                引数のリストが予約受付状況情報なら辞書にして返す

        """
        status_data = dict()
        row = list(map(lambda x: self.format_string(x), row))
        try:
            area = row[0].replace(" ", "")
            # 地区の文字列が正しくない箇所があるので正しい文字列に置換する。
            if (
                area == "各条１７～２７丁目・宮前・南地区"
                or area == "各条１７～２８丁目・宮前・南地区"
                or area == "各条１７～２９丁目・宮前・南地区"
                or area == "各条１７～３０丁目・宮前・南地区"
                or area == "各条１７～３１丁目・宮前・南地区"
            ):
                area = "各条１７～２６丁目・宮前・南地区"

            family = self.get_available(row[8])
            not_family = self.get_available(row[9])
            suberb = self.get_available(row[10])
            is_target_family = family["available"]
            is_target_not_family = not_family["available"]
            is_target_suberb = suberb["available"]
            memo = family["text"] + " " + not_family["text"] + " " + row[12]
            memo = memo.strip()
            status = row[5].replace("―", "")
            # 予約受付状況が空欄の場合、備考の値をセットする。
            if status == "":
                status = memo
                memo = ""

            status_data = {
                "area": area,
                "medical_institution_name": row[1].replace(" ", ""),
                "address": row[2],
                "phone_number": row[3],
                "vaccine": row[4],
                "status": status,
                "inoculation_time": row[6].replace("―", ""),
                "target_age": row[7].replace("―", ""),
                "is_target_family": is_target_family,
                "is_target_not_family": is_target_not_family,
                "is_target_suberb": is_target_suberb,
                "target_other": row[11].replace("―", ""),
                "memo": memo,
            }
            return status_data
        except (IndexError, ValueError):
            return None

    @staticmethod
    def get_available(target_string: str) -> dict:
        """文字列が対象、対象外のどちらを表しているか判定

        かかりつけ、かかりつけ以外の文字列から対象なのかどうかを判定し、
        付記があればその文字列を取得する。

        Args:
            target_string (str): ○を含む可能性のある文字列

        Returns:
            result (dict): 判定結果辞書
                ○が含まれてたらavailableキーに真をセット、
                textキーに付記文字列があればセット。

        """
        if not isinstance(target_string, str):
            return {"available": False, "text": ""}

        ok_match = re.search("^(.*)○(.*)$", target_string)
        ng_match = re.search("^(.*)×(.*)$", target_string)
        family_text = ""
        if ok_match:
            family_text = ok_match.group(1) + ok_match.group(2)
            return {"available": True, "text": family_text}
        elif ng_match:
            family_text = ng_match.group(1) + ng_match.group(2)
            return {"available": False, "text": family_text}
        else:
            return {"available": None, "text": ""}

    def get_medical_institution_list(self) -> list:
        """スクレイピング結果から主キーとなる医療機関名のリストを取得

        Returns:
            medical_institutione_list (list of tuple): 医療機関名のリスト
                スクレイピングした医療機関名とワクチン種類のタプルをリストで返す。

        """
        medical_institution_list = list()
        for reservation_status in self.lists:
            medical_institution_list.append(
                (
                    reservation_status["medical_institution_name"],
                    reservation_status["vaccine"],
                )
            )
        return medical_institution_list
