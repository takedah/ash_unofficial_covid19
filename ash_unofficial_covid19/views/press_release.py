from datetime import date, datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from ..errors import DatabaseConnectionError
from ..services.database import ConnectionPool
from ..services.press_release_link import PressReleaseLinkService
from ..views.view import View


class PressReleaseView(View):
    """旭川市新型コロナウイルス感染症報道発表日データ

    旭川市新型コロナウイルス感染症報道発表日データをFlaskへ渡すデータにする

    Attributes:
        latest_date (date): 最新の報道発表日

    """

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        self.__latest_date = self._get_latest_date(pool)

    @property
    def latest_date(self):
        return self.__latest_date

    def _get_latest_date(self, pool: ConnectionPool) -> date:
        """最新の報道発表日の日付を返す

        Args:
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        Returns:
            latest_date (date): 最新の報道発表日の日付データ

        """
        now = datetime.now(timezone(timedelta(hours=+9), "JST"))
        try:
            press_release_link_service = PressReleaseLinkService(pool)
            latest_date = press_release_link_service.get_latest_publication_date()
        except DatabaseConnectionError:
            # エラーが起きた場合現在日付を基準とする。
            # このとき市の発表が16時になることが多いので16時より前なら前日を基準とする。
            latest_date = now.date()
            if now.hour < 16:
                latest_date = latest_date - relativedelta(days=1)

        return latest_date
