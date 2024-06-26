class Error(Exception):
    """エラーを発生させる処理

    Attributes:
        message (str): エラーメッセージ

    """

    def __init__(self, message):
        self.__message = message

    @property
    def message(self):
        return self.__message


class DatabaseConnectionError(Error):
    """データベース接続に関するエラー

    Attributes:
        message (str): エラーメッセージ

    """

    def __init__(self, message):
        Error.__init__(self, message)


class ServiceError(Error):
    """SQL実行に関するエラー

    Attributes:
        message (str): エラーメッセージ

    """

    def __init__(self, message):
        Error.__init__(self, message)


class HTTPDownloadError(Error):
    """Webページのスクレイピングに関するエラー

    Attributes:
        message (str): エラーメッセージ

    """

    def __init__(self, message):
        Error.__init__(self, message)


class DataModelError(Error):
    """データモデルの生成に関するエラー

    Attributes:
        message (str): エラーメッセージ

    """

    def __init__(self, message):
        Error.__init__(self, message)
