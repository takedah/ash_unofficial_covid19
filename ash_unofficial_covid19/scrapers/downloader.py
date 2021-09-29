from abc import ABCMeta, abstractmethod
from io import BytesIO, StringIO
from json import JSONDecodeError

import requests
from requests import HTTPError, Timeout
from urllib3.exceptions import MaxRetryError

from ..errors import HTTPDownloadError
from ..logs import AppLog


class Downloader(metaclass=ABCMeta):
    """Webからコンテンツをダウンロードするクラスの基底クラス"""

    def __init__(self):
        self.__logger = AppLog()

    @property
    @abstractmethod
    def content(self):
        pass

    @property
    @abstractmethod
    def url(self):
        pass

    def info_log(self, message: str) -> None:
        """AppLog.infoのラッパー

        Args:
            message (str): 通常のログメッセージ

        """
        if isinstance(message, str):
            self.__logger.info(message)
        else:
            self.__logger.info("通常メッセージの指定が正しくない")

    def error_log(self, message: str) -> None:
        """AppLog.errorのラッパー

        Args:
            message (str): エラーログメッセージ

        """
        if isinstance(message, str):
            self.__logger.error(message)
        else:
            self.__logger.info("エラーメッセージの指定が正しくない")


class DownloadedHTML(Downloader):
    """HTMLファイルのbytesデータの取得

    WebサイトからHTMLファイルをダウンロードしてbytesデータに変換する。

    Attributes:
        content (bytes): ダウンロードしたHTMLファイルのbytesデータ
        url (str): HTMLファイルのURL

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): WebサイトのHTMLファイルのURL

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_html_content(self.__url)

    @property
    def content(self) -> bytes:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_html_content(self, url: str) -> bytes:
        """WebサイトからHTMLファイルのbytesデータを取得

        Args:
            url (str): HTMLファイルのURL

        Returns:
            content (bytes): ダウンロードしたHTMLファイルのbytesデータ

        """
        try:
            # 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて
            # 回避する
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
            response = requests.get(url)
            self.info_log("HTMLファイルのダウンロードに成功しました。")
        except (ConnectionError, MaxRetryError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)
        if response.status_code != 200:
            message = "cannot get HTML contents."
            self.error_log(message)
            raise HTTPDownloadError(message)
        return response.content


class DownloadedCSV(Downloader):
    """CSVファイルのStringIOデータの取得

    WebサイトからCSVファイルをダウンロードしてStringIOで返す

    Attributes:
        content (StringIO): ダウンロードしたCSVファイルのStringIOデータ
        url (str): ダウンロードしたCSVファイルのURL

    """

    def __init__(self, url: str, encoding: str = "utf-8"):
        """
        Args:
            url (str): WebサイトのCSVファイルのURL
            encoding (str): CSVファイルの文字コード

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_csv_content(url=self.__url, encoding=encoding)

    @property
    def content(self) -> StringIO:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_csv_content(self, url: str, encoding: str) -> StringIO:
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
            self.info_log("CSVファイルのダウンロードに成功しました。")
        except (ConnectionError, MaxRetryError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)
        if response.status_code != 200:
            message = "cannot get CSV contents."
            self.error_log(message)
            raise HTTPDownloadError(message)
        return csv_io


class DownloadedPDF(Downloader):
    """PDFファイルのBytesIOデータの取得

    WebサイトからPDFファイルをダウンロードしてBytesIOで返す

    Attributes:
        content (BytesIO): ダウンロードしたPDFファイルのBytesIOデータ
        url (str): ダウンロードしたPDFファイルのURL

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): WebサイトのPDFファイルのURL

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_pdf_content(self.__url)

    @property
    def content(self) -> BytesIO:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_pdf_content(self, url: str) -> BytesIO:
        """WebサイトからCSVファイルのBytesIOデータを取得

        Args:
            url (str): PDFファイルのURL

        Returns:
            pdf_io (BytesIO): ワクチン接種医療機関一覧PDFデータから抽出したデータ

        """
        try:
            # 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて
            # 回避する
            requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
            response = requests.get(url)
            self.info_log("PDFファイルのダウンロードに成功しました。")
        except (ConnectionError, MaxRetryError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)

        if response.status_code != 200:
            message = "cannot get PDF contents."
            self.error_log(message)
            raise HTTPDownloadError(message)

        return BytesIO(response.content)


class DownloadedJSON(Downloader):
    """Web APIからJSONデータの取得

    WebサイトからJSONファイルをダウンロードして辞書データに変換する。

    Attributes:
        content (bytes): ダウンロードしたJSONファイルの辞書データ
        url (str): ダウンロードしたJSONファイルのURL

    """

    def __init__(self, url: str):
        """
        Args:
            url (str): WebサイトのJSONファイルのURL

        """
        Downloader.__init__(self)
        self.__url = url
        self.__content = self._get_json_content(self.__url)

    @property
    def content(self) -> dict:
        return self.__content

    @property
    def url(self) -> str:
        return self.__url

    def _get_json_content(self, url: str) -> dict:
        """WebサイトからJSONファイルの辞書データを取得

        Args:
            url (str): JSONファイルのURL

        Returns:
            content (dict): ダウンロードしたHTMLファイルのbytesデータ

        """
        try:
            response = requests.get(url)
            self.info_log("JSONファイルのダウンロードに成功しました。")
        except (ConnectionError, MaxRetryError, Timeout, HTTPError):
            message = "cannot connect to web server."
            self.error_log(message)
            raise HTTPDownloadError(message)

        if response.status_code != 200:
            message = "cannot get HTML contents."
            self.error_log(message)
            raise HTTPDownloadError(message)

        try:
            json_res = response.json()
        except JSONDecodeError:
            message = "cannot decode json response."
            self.error_log(message)
            raise HTTPDownloadError(message)

        return json_res
