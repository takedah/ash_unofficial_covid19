from datetime import date, datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from ..errors import DatabaseConnectionError
from ..services.press_release_link import PressReleaseLinkService
from ..views.view import View


class PressReleaseView(View):
    """旭川市新型コロナウイルス感染症報道発表日データ

    旭川市新型コロナウイルス感染症報道発表日データをFlaskへ渡すデータにする

    Attributes:
        latest_date (date): 最新の報道発表日

    """

    def __init__(self):
        self.__latest_date = self._get_latest_date()

    @property
    def latest_date(self):
        return self.__latest_date

    @staticmethod
    def _get_latest_date() -> date:
        """最新の報道発表日の日付を返す

        Returns:
            latest_date (date): 最新の報道発表日の日付データ

        """
        now = datetime.now(timezone(timedelta(hours=+9), "JST"))
        try:
            press_release_link_service = PressReleaseLinkService()
            latest_date = press_release_link_service.get_latest_publication_date()
        except DatabaseConnectionError:
            # エラーが起きた場合現在日付を基準とする。
            # このとき市の発表が16時になることが多いので16時より前なら前日を基準とする。
            latest_date = now.date()
            if now.hour < 16:
                latest_date = latest_date - relativedelta(days=1)

        return latest_date
