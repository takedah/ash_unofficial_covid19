from ..services.reservation_status import ReservationStatusService
from ..views.view import View


class ReservationStatusView(View):
    """旭川市新型コロナワクチン接種医療機関予約受付状況データ

    旭川市新型コロナワクチン接種医療機関予約受付状況データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = ReservationStatusService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self):
        return self.__last_updated

    def find(self) -> list:
        """
        新型コロナワクチン接種医療機関の予約受付状況全件のリストを返す

        Returns:
            res (list of tuple): 医療機関の予約受付状況一覧リスト
                医療機関予約受付状況データオブジェクトと医療機関名称をURLエンコードした文字列を対にしたタプルのリスト

        """
        return self.__service.find()
