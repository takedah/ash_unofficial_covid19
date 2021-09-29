from .config import Config
from .errors import DatabaseConnectionError, HTTPDownloadError, ServiceError
from .models.reservation_status import ReservationStatusFactory
from .scrapers.reservation_status import ScrapeReservationStatus
from .services.reservation_status import ReservationStatusService


def import_reservation_statuses(url: str) -> None:
    """
    旭川市公式ホームページから新型コロナワクチン接種医療機関の予約受付状況一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): ワクチン接種医療機関の予約受付状況一覧PDFファイルのURL

    """
    factory = ReservationStatusFactory()

    try:
        scraped_data = ScrapeReservationStatus(url)
    except HTTPDownloadError as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        factory.create(**row)

    service = ReservationStatusService()
    try:
        service.create(factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def delete_non_exist_data(url: str) -> None:
    """スクレイピングしたデータに存在しない登録済み医療機関の予約受付状況データを削除する

    Args:
        url (str): ワクチン接種医療機関の予約受付状況一覧PDFファイルのURL

    """
    scraped_data = ScrapeReservationStatus(url)
    new_name_list = scraped_data.get_name_list()
    service = ReservationStatusService()
    current_name_list = service.get_name_list()
    non_exist_names = list(set(current_name_list) - set(new_name_list))
    for non_exist_name in non_exist_names:
        service.delete(non_exist_name)


if __name__ == "__main__":
    import_reservation_statuses(Config.RESERVATION_STATUSES_URL)
    delete_non_exist_data(Config.RESERVATION_STATUSES_URL)
