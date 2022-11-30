import time

from .config import Config
from .errors import DatabaseConnectionError, HTTPDownloadError, ScrapeError, ServiceError
from .models.baby_reservation_status import BabyReservationStatusFactory
from .models.child_reservation_status import ChildReservationStatusFactory
from .models.first_reservation_status import FirstReservationStatusFactory
from .models.location import LocationFactory
from .models.reservation_status import ReservationStatusFactory
from .scrapers.baby_reservation_status import ScrapeBabyReservationStatus
from .scrapers.child_reservation_status import ScrapeChildReservationStatus
from .scrapers.first_reservation_status import ScrapeFirstReservationStatus
from .scrapers.location import ScrapeYOLPLocation
from .scrapers.reservation_status import ScrapeReservationStatus
from .services.baby_reservation_status import BabyReservationStatusService
from .services.child_reservation_status import ChildReservationStatusService
from .services.database import ConnectionPool
from .services.first_reservation_status import FirstReservationStatusService
from .services.location import LocationService
from .services.reservation_status import ReservationStatusService

conn = ConnectionPool()


def import_reservation_statuses(html_url: str) -> None:
    """
    旭川市公式ホームページから新型コロナワクチン接種医療機関の予約受付状況一覧を取得し、
    データベースへ格納する。

    Args:
        html_url (str): ワクチン接種医療機関予約受付状況HTMLファイルのURL

    """
    factory = ReservationStatusFactory()

    try:
        scraped_data = ScrapeReservationStatus(html_url)
        new_name_list = scraped_data.get_medical_institution_list()
    except HTTPDownloadError as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        factory.create(**row)

    service = ReservationStatusService(conn)
    current_name_list = service.get_medical_institution_list()
    added_names = list()
    for new_name in new_name_list:
        if new_name not in current_name_list:
            added_names.append(new_name[0])

    added_names = list(set(added_names))

    deleted_names = list()
    for current_name in current_name_list:
        if current_name not in new_name_list:
            deleted_names.append((current_name[0], current_name[1]))

    try:
        service.create(factory)
        import_locations(added_names)
        for deleted_name in deleted_names:
            service.delete(deleted_name)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return

    return


def import_first_reservation_statuses(html_url: str) -> None:
    """
    旭川市公式ホームページから新型コロナワクチン1・2回目接種医療機関の予約受付状況一覧を取得し、
    データベースへ格納する。

    Args:
        html_url (str): ワクチン接種医療機関予約受付状況HTMLファイルのURL

    """
    factory = FirstReservationStatusFactory()

    try:
        scraped_data = ScrapeFirstReservationStatus(html_url)
        new_name_list = scraped_data.get_medical_institution_list()
    except HTTPDownloadError as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        factory.create(**row)

    service = FirstReservationStatusService(conn)
    current_name_list = service.get_medical_institution_list()
    added_names = list()
    for new_name in new_name_list:
        if new_name not in current_name_list:
            added_names.append(new_name)

    added_names = list(set(added_names))

    deleted_names = list()
    for current_name in current_name_list:
        if current_name not in new_name_list:
            deleted_names.append(current_name)

    try:
        service.create(factory)
        import_locations(added_names)
        for deleted_name in deleted_names:
            service.delete(deleted_name)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return

    return


def import_child_reservation_statuses(html_url: str) -> None:
    """
    旭川市公式ホームページから新型コロナワクチン接種医療機関の予約受付状況一覧を取得し、
    データベースへ格納する。

    Args:
        html_url (str): ワクチン接種医療機関予約受付状況HTMLファイルのURL

    """
    factory = ChildReservationStatusFactory()

    try:
        scraped_data = ScrapeChildReservationStatus(html_url)
        new_name_list = scraped_data.get_medical_institution_list()
    except HTTPDownloadError as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        factory.create(**row)

    service = ChildReservationStatusService(conn)
    current_name_list = service.get_medical_institution_list()
    added_names = list()
    for new_name in new_name_list:
        if new_name not in current_name_list:
            added_names.append(new_name[0])

    added_names = list(set(added_names))

    deleted_names = list()
    for current_name in current_name_list:
        if current_name not in new_name_list:
            deleted_names.append((current_name[0], current_name[1]))

    try:
        service.create(factory)
        import_locations(added_names)
        for deleted_name in deleted_names:
            service.delete(deleted_name)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return

    return


def import_baby_reservation_statuses(html_url: str) -> None:
    """
    旭川市公式ホームページから新型コロナワクチン接種医療機関の予約受付状況一覧を取得し、
    データベースへ格納する。

    Args:
        html_url (str): ワクチン接種医療機関予約受付状況HTMLファイルのURL

    """
    factory = BabyReservationStatusFactory()

    try:
        scraped_data = ScrapeBabyReservationStatus(html_url)
        new_name_list = scraped_data.get_medical_institution_list()
    except HTTPDownloadError as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        factory.create(**row)

    service = BabyReservationStatusService(conn)
    current_name_list = service.get_medical_institution_list()
    added_names = list()
    for new_name in new_name_list:
        if new_name not in current_name_list:
            added_names.append(new_name[0])

    added_names = list(set(added_names))

    deleted_names = list()
    for current_name in current_name_list:
        if current_name not in new_name_list:
            deleted_names.append((current_name[0], current_name[1]))

    try:
        service.create(factory)
        import_locations(added_names)
        for deleted_name in deleted_names:
            service.delete(deleted_name)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return

    return


def import_locations(medical_institution_name_list: list) -> None:
    """
    医療機関の名称一覧から緯度経度を取得し、データベースへ格納する。

    Args:
        medical_institution_name_list (list): 医療機関名リスト

    """
    locations_factory = LocationFactory()
    for medical_institution_name in medical_institution_name_list:
        try:
            scraped_data = ScrapeYOLPLocation(medical_institution_name)
        except (HTTPDownloadError, ScrapeError):
            continue

        # 1番目の検索結果を採用する
        row = scraped_data.lists[0]
        locations_factory.create(**row)
        time.sleep(1)

    service = LocationService(conn)
    try:
        service.create(locations_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)

    # YOLPで緯度経度を取得できなかった医療機関に手動で情報を追加
    add_locations_factory = LocationFactory()
    add_data_list = [
        {
            "medical_institution_name": "やまきた内科",
            "longitude": 142.3820653407415,
            "latitude": 43.726742625984095,
        },
        {
            "medical_institution_name": "グリート永山循環器・むくみクリニック",
            "longitude": 142.4062653980119,
            "latitude": 43.78568808811868,
        },
        {
            "medical_institution_name": "フクダクリニック",
            "longitude": 142.38243298115825,
            "latitude": 43.81521459576975,
        },
        {
            "medical_institution_name": "佐藤内科医院",
            "longitude": 142.39588151965012,
            "latitude": 43.76034860571178,
        },
        {
            "medical_institution_name": "唐沢病院",
            "longitude": 142.36361116952028,
            "latitude": 43.76824898808485,
        },
        {
            "medical_institution_name": "岩田医院",
            "longitude": 142.36924956957841,
            "latitude": 43.76624333505984,
        },
        {
            "medical_institution_name": "旭川キュアメディクス",
            "longitude": 142.37285062533863,
            "latitude": 43.76773531393752,
        },
        {
            "medical_institution_name": "東旭川病院",
            "longitude": 142.4377094983569,
            "latitude": 43.777870139580855,
        },
        {
            "medical_institution_name": "永山腎泌尿器科クリニック",
            "longitude": 142.40852307102085,
            "latitude": 43.79484919172041,
        },
        {
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "longitude": 142.3815237271935,
            "latitude": 43.798826491523464,
        },
        {
            "medical_institution_name": "旭川医科大学病院",
            "longitude": 142.38382199835564,
            "latitude": 43.73007572101459,
        },
        {
            "medical_institution_name": "旭川リハビリテーション病院",
            "longitude": 142.3871075983558,
            "latitude": 43.73051097382853,
        },
        {
            "medical_institution_name": "かむいクリニック",
            "longitude": 142.34020758985673,
            "latitude": 43.75035378612844,
        },
        {
            "medical_institution_name": "小児科くさのこどもクリニック",
            "longitude": 142.390319166667,
            "latitude": 43.805724166667,
        },
        {
            "medical_institution_name": "ながのクリニック",
            "longitude": 142.396569444444,
            "latitude": 43.744830833333,
        },
        {
            "medical_institution_name": "旭川消化器肛門クリニック",
            "longitude": 142.387003055556,
            "latitude": 43.803429722222,
        },
        {
            "medical_institution_name": "のむらひふ科耳鼻咽喉科甲状腺クリニック",
            "longitude": 142.381543888889,
            "latitude": 43.727218333333,
        },
        {
            "medical_institution_name": "いいだメンタルペインクリニック",
            "longitude": 142.36001636896643,
            "latitude": 43.76306331601826,
        },
        {
            "medical_institution_name": "みやざき内科小児科クリニック",
            "longitude": 142.38439872663736,
            "latitude": 43.801697594258115,
        },
        {
            "medical_institution_name": "みうら小児科クリニック",
            "longitude": 142.33471821314035,
            "latitude": 43.75955680467453,
        },
    ]
    for add_data in add_data_list:
        add_locations_factory.create(**add_data)

    try:
        service.create(add_locations_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)

    return


if __name__ == "__main__":
    try:
        import_reservation_statuses(Config.RESERVATION_STATUSES_URL)
        import_first_reservation_statuses(Config.RESERVATION_STATUSES_URL)
        import_child_reservation_statuses(Config.RESERVATION_STATUSES_URL)
        import_baby_reservation_statuses(Config.RESERVATION_STATUSES_URL)
    finally:
        conn.close_connection()
