from typing import Optional

from ..scrapers.reservation_status import ScrapeReservationStatus


class ScrapeBabyReservationStatus(ScrapeReservationStatus):
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
        self.__lists = list()
        downloaded_html = self.get_html(html_url)
        table_data = self.get_table_data(downloaded_html, "tablepress-20-no-2")
        for row in table_data:
            extracted_data = self._extract_status_data(row)
            if extracted_data:
                self.__lists.append(extracted_data)

    @property
    def lists(self) -> list:
        return self.__lists

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

            family = self.get_available(row[6])
            not_family = self.get_available(row[7])
            suberb = self.get_available(row[8])
            is_target_family = family["available"]
            is_target_not_family = not_family["available"]
            is_target_suberb = suberb["available"]
            memo = family["text"] + " " + not_family["text"] + " " + row[9]
            memo = memo.strip()
            status = row[4].replace("―", "")
            # 予約受付状況が空欄の場合、備考の値をセットする。
            if status == "":
                status = memo
                memo = ""

            status_data = {
                "area": area,
                "medical_institution_name": row[1].replace(" ", ""),
                "address": row[2],
                "phone_number": row[3],
                "vaccine": "",
                "status": status,
                "inoculation_time": row[5].replace("―", ""),
                "target_age": "",
                "is_target_family": is_target_family,
                "is_target_not_family": is_target_not_family,
                "is_target_suberb": is_target_suberb,
                "target_other": "",
                "memo": memo,
            }
            return status_data
        except (IndexError, ValueError):
            return None