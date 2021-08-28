import urllib.parse

from flask import escape

from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.scrapers.downloader import DownloadedJSON
from ash_unofficial_covid19.scrapers.scraper import Scraper


class ScrapeYOLPLocation(Scraper):
    """Yahoo! Open Local Platform (YOLP) Web APIから指定した施設の緯度経度情報を取得

    Attributes:
        lists (list of dict): 緯度経度データを表す辞書のリスト

    """

    def __init__(self, facility_name: str):
        """
        Args:
            facility_name (str): 緯度経度情報を取得したい施設の名称

        """
        self.__lists = list()
        if isinstance(facility_name, str):
            facility_name = urllib.parse.quote(escape(facility_name))
        else:
            raise TypeError("施設名の指定が正しくありません。")

        city_code = "01204"
        industry_code = "0401"
        if Config.YOLP_APP_ID:
            app_id = Config.YOLP_APP_ID
        else:
            raise RuntimeError("YOLPアプリケーションIDの指定が正しくありません。")

        json_url = (
            Config.YOLP_BASE_URL
            + "?appid="
            + app_id
            + "&query="
            + facility_name
            + "&ac="
            + city_code
            + "&gc="
            + industry_code
            + "&sort=-match&detail=simple&output=json"
        )
        downloaded_json = self._get_json(json_url)
        for search_result in self._get_search_results(downloaded_json):
            location_data = self._extract_location_data(search_result)
            location_data["medical_institution_name"] = urllib.parse.unquote(
                facility_name
            )
            self.__lists.append(location_data)

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_json(self, json_url: str) -> DownloadedJSON:
        """JSONデータを要素に持つオブジェクトを返す

        Args:
            json_url (str): YOLP Web APIのURL

        Returns:
            downloaded_json (:obj:`DownloadedJSON`): JSONデータを要素に持つオブジェクト

        """
        if isinstance(json_url, str):
            return DownloadedJSON(json_url)
        else:
            raise TypeError("Web API URLの指定が正しくありません。")

    def _get_search_results(self, downloaded_json: DownloadedJSON) -> list:
        """YOLP Web APIの返すJSONデータから検索結果データを抽出

        Args:
            downloaded_json (:obj:`DownloadedJSON`): JSONデータを要素に持つオブジェクト

        Returns:
            search_results (list of dict): 検索結果辞書データリスト
                JSONデータから検索結果の部分を辞書データで抽出したリスト

        """
        json_res = downloaded_json.content
        try:
            if json_res["ResultInfo"]["Count"] == 0:
                # 検索結果が0件の場合、緯度経度にダミーの値をセットして返す
                search_results = [
                    {
                        "Geometry": {
                            "Coordinates": "0,0",
                        },
                    },
                ]
            else:
                search_results = json_res["Feature"]
            return search_results
        except KeyError:
            raise RuntimeError("期待したJSONレスポンスが得られていません。")

    def _extract_location_data(self, search_result: dict) -> dict:
        """YOLP Web APIの返すJSONデータから緯度経度情報を抽出

        Args:
            yolp_json (dict): YOLP Web APIの返すJSONデータ

        Returns:
            location_data (dict): 緯度経度の辞書データ

        """
        location_data = dict()
        coordinates = search_result["Geometry"]["Coordinates"].split(",")
        location_data["longitude"] = float(coordinates[0])
        location_data["latitude"] = float(coordinates[1])
        return location_data
