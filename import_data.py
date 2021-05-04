from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.errors import (
    DatabaseError,
    DataError,
    DataModelError,
    HTTPDownloadError
)
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.models import (
    AsahikawaPatientFactory,
    HokkaidoPatientFactory
)
from ash_unofficial_covid19.scraper import (
    DownloadedHTML,
    ScrapedCSVData,
    ScrapedHTMLData
)
from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    HokkaidoPatientService
)


def import_hokkaido_data(url: str) -> bool:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL

    Returns:
        bool: データベースへ格納が成功したら真を返す

    """
    logger = AppLog()
    try:
        scraped_data = ScrapedCSVData(url)
    except HTTPDownloadError as e:
        logger.warning(e.message)
        return False

    patients_data = HokkaidoPatientFactory()
    for row in scraped_data.patients_data:
        patients_data.create(**row)

    try:
        conn = DB()
        service = HokkaidoPatientService(conn)
        for patient in patients_data.items:
            service.create(patient)
        conn.commit()
        conn.close()
    except (DataError, DatabaseError, DataModelError) as e:
        conn.close()
        logger.warning(e.message)
        return False

    logger.info("北海道のデータ登録処理が完了しました。")
    return True


def import_asahikawa_data(url: str, target_year: int) -> bool:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL
        target_year (int): 対象年

    Returns:
        bool: データベースへ格納が成功したら真を返す

    """
    logger = AppLog()
    try:
        html_data = DownloadedHTML(url)
    except HTTPDownloadError as e:
        logger.warning(e.message)
        return False

    scraped_data = ScrapedHTMLData(downloaded_html=html_data, target_year=target_year)
    patients_data = AsahikawaPatientFactory()
    for row in scraped_data.patients_data:
        patients_data.create(**row)

    try:
        conn = DB()
        service = AsahikawaPatientService(conn)
        for patient in patients_data.items:
            service.create(patient)
        conn.commit()
        conn.close()
    except (DataError, DatabaseError, DataModelError) as e:
        conn.close()
        logger.warning(e.message)
        return False

    logger.info("旭川市のデータ登録処理が完了しました。")
    return True


def delete_duplicate_data() -> bool:
    """
    旭川市公式ホームページから取得した新型コロナウイルス感染症の感染者情報には、
    重複した事例が掲載されたままのため、当該データを削除する。

    Returns:
        bool: 削除が成功したら真を返す

    """
    logger = AppLog()
    try:
        conn = DB()
        service = AsahikawaPatientService(conn)
        for duplicate_patient_number in service.get_duplicate_patient_numbers():
            service.delete(patient_number=duplicate_patient_number)
        conn.commit()
        conn.close()
    except (DataError, DatabaseError) as e:
        conn.close()
        logger.warning(e.message)
        return False

    logger.info("重複事例のデータ削除処理が完了しました。")
    return True


if __name__ == "__main__":
    import_hokkaido_data(Config.HOKKAIDO_URL)
    import_asahikawa_data(Config.LATEST_DATA_URL, 2021)
    import_asahikawa_data(Config.APR2021_DATA_URL, 2021)
    import_asahikawa_data(Config.MAR2021_DATA_URL, 2021)
    import_asahikawa_data(Config.FEB2021_DATA_URL, 2021)
    import_asahikawa_data(Config.JAN2021_DATA_URL, 2021)
    import_asahikawa_data(Config.DEC2020_DATA_URL, 2020)
    import_asahikawa_data(Config.NOV2020_OR_EARLIER_URL, 2020)
    delete_duplicate_data()
