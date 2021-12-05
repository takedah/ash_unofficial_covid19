import urllib.parse

from ..models.reservation_status_location import ReservationStatusLocation
from ..services.reservation_status_location import ReservationStatusLocationService
from ..views.view import View


class ReservationStatusView(View):
    """旭川市新型コロナワクチン接種医療機関予約受付状況データ

    旭川市新型コロナワクチン接種医療機関予約受付状況データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = ReservationStatusLocationService(is_third_time=True)
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self):
        return self.__last_updated

    def find(self, medical_institution_name: str) -> ReservationStatusLocation:
        """位置情報、予約受付情報付き新型コロナワクチン接種医療機関情報

        指定した対象年齢の新型コロナワクチン接種医療機関の一覧に医療機関の位置情報と
        予約受付情報を付けて返す

        Args:
            medical_institution_name (str): 医療機関の名称

        Returns:
            results (:obj:`ReservationStatusLocation`): 医療機関データ
                新型コロナワクチン接種医療機関予約受付情報の情報に緯度経度を含めた
                データオブジェクト

        """
        return self.__service.find(medical_institution_name=medical_institution_name)

    def find_all(self) -> list:
        """
        新型コロナワクチン接種医療機関の予約受付状況全件のリストを返す

        Returns:
            res (list of tuple): 医療機関の予約受付状況一覧リスト
                医療機関予約受付状況データオブジェクトと医療機関名称をURLエンコードした文字列を対にしたタプルのリスト

        """
        res = list()
        reservation_statuses = self.__service.find_all()
        for reservation_status in reservation_statuses.items:
            res.append(
                (
                    reservation_status,
                    urllib.parse.quote(reservation_status.medical_institution_name),
                )
            )
        return res
