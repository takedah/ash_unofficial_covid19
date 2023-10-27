import time

from .config import Config
from .errors import DatabaseConnectionError, HTTPDownloadError, ScrapeError, ServiceError
from .models.location import LocationFactory
from .models.outpatient import OutpatientFactory
from .scrapers.location import ScrapeOpendataLocation, ScrapeYOLPLocation
from .scrapers.outpatient import ScrapeOutpatient
from .scrapers.outpatient_link import ScrapeOutpatientLink
from .services.database import ConnectionPool
from .services.location import LocationService
from .services.outpatient import OutpatientService

conn = ConnectionPool()


def import_outpatients(html_url: str) -> None:
    """
    北海道公式ホームページから新型コロナ発熱外来一覧を取得し、
    データベースへ格納する。

    Args:
        html_url (str): 北海道ホームページのURL

    """
    factory = OutpatientFactory()
    source = ScrapeOutpatientLink(html_url)

    try:
        scraped_data = ScrapeOutpatient(source.lists[0]["url"])
        new_name_list = scraped_data.get_medical_institution_list()
    except HTTPDownloadError as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        factory.create(**row)

    service = OutpatientService(conn)
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
            "medical_institution_name": "医療法人社団旭豊会 旭川三愛病院",
            "longitude": 142.408792,
            "latitude": 43.792291,
        },
        {
            "medical_institution_name": "あさひかわ駅前内科",
            "longitude": 142.3600949,
            "latitude": 43.7628769,
        },
    ]
    for add_data in add_data_list:
        add_locations_factory.create(**add_data)

    try:
        service.create(add_locations_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)

    return


def import_locations_from_opendata(csv_url: str) -> None:
    """
    北海道オープンデータポータルのCSVデータから医療機関の緯度経度を取得し、データベースへ格納する。

    Args:
        csv_url (str): 北海道オープンデータポータルのCSVファイルのURL

    """
    locations_factory = LocationFactory()
    try:
        scraped_data = ScrapeOpendataLocation(csv_url)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        locations_factory.create(**row)

    service = LocationService(conn)
    try:
        service.create(locations_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)

    return


if __name__ == "__main__":
    try:
        import_outpatients(Config.OUTPATIENTS_URL)
        import_locations_from_opendata(Config.HOSPITAL_OPENDATA_URL)
        import_locations_from_opendata(Config.CLINIC_OPENDATA_URL)
    finally:
        conn.close_connection()
