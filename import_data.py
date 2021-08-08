from datetime import date
from typing import Optional

from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.errors import (
    DatabaseConnectionError,
    DataModelError,
    HTTPDownloadError,
    ServiceError
)
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.models import (
    AsahikawaPatientFactory,
    HokkaidoPatientFactory,
    MedicalInstitutionFactory
)
from ash_unofficial_covid19.scraper import (
    DownloadedCSV,
    DownloadedHTML,
    ScrapeAsahikawaPatients,
    ScrapeHokkaidoPatients,
    ScrapeMedicalInstitutions
)
from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    HokkaidoPatientService,
    MedicalInstitutionService
)

logger = AppLog()


def import_hokkaido_data(url: str) -> bool:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL

    Returns:
        bool: データベースへ格納が成功したら真を返す

    """
    try:
        csv_data = DownloadedCSV(url=url, encoding="cp932")
    except HTTPDownloadError as e:
        logger.warning(e.message)
        return False

    scraped_data = ScrapeHokkaidoPatients(csv_data)
    patients_data = HokkaidoPatientFactory()
    for row in scraped_data.lists:
        patients_data.create(**row)

    try:
        service = HokkaidoPatientService()
        service.create(patients_data)
    except (DatabaseConnectionError, ServiceError, DataModelError) as e:
        logger.warning(e.message)
        return False

    logger.info("北海道のデータ登録処理が完了しました。")
    return True


def get_asahikawa_data(url: str, target_year: int) -> Optional[ScrapeAsahikawaPatients]:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報一覧を取得する。

    Args:
        url (str): 旭川市公式ホームページのURL
        target_year (int): 対象年

    Returns:
        scraped_data (obj:`ScrapedHTMLData`): ダウンロードしたHTMLデータ

    """
    try:
        html_data = DownloadedHTML(url)
    except HTTPDownloadError as e:
        logger.warning(e.message)
        return None

    return ScrapeAsahikawaPatients(downloaded_html=html_data, target_year=target_year)


def import_asahikawa_data(download_lists: list) -> bool:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を、
    データベースへ格納する。

    Args:
        download_lists (list of tuple): スクレイピング対象URLとデータの対象年を要素に
            持つタプルを要素としたリスト

    Returns:
        bool: データベースへ格納が成功したら真を返す

    """
    patients_data = AsahikawaPatientFactory()
    for download_list in download_lists:
        url = download_list[0]
        target_year = download_list[1]
        scraped_data = get_asahikawa_data(url=url, target_year=target_year)
        if scraped_data:
            for row in scraped_data.lists:
                patients_data.create(**row)

    # HTMLに市内番号489の掲載が抜けているので手動で追加する
    additional_data = {
        "patient_number": 489,
        "city_code": "012041",
        "prefecture": "北海道",
        "city_name": "旭川市",
        "publication_date": date(2020, 12, 1),
        "onset_date": None,
        "residence": "旭川市",
        "age": "40代",
        "sex": "男性",
        "occupation": "",
        "status": "",
        "symptom": "",
        "overseas_travel_history": None,
        "be_discharged": None,
        "note": "北海道発表No.;9049;周囲の患者の発生;No.488;濃厚接触者の状況;調査中;",
        "hokkaido_patient_number": 9049,
        "surrounding_status": "No.488",
        "close_contact": "調査中",
    }
    patients_data.create(**additional_data)

    try:
        service = AsahikawaPatientService()
        service.create(patients_data)
    except (DatabaseConnectionError, ServiceError, DataModelError) as e:
        logger.warning(e.message)
        return False

    logger.info("旭川市のデータ登録処理が完了しました。")
    return True


def import_medical_institutions_data(url: str) -> bool:
    """
    旭川市公式ホームページから新型コロナワクチン接種医療機関一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL

    Returns:
        bool: データベースへ格納が成功したら真を返す

    """
    try:
        html_content = DownloadedHTML(url)
    except HTTPDownloadError as e:
        logger.warning(e.message)
        return False

    scraped_data = ScrapeMedicalInstitutions(html_content)
    medical_institutions_data = MedicalInstitutionFactory()
    for row in scraped_data.lists:
        medical_institutions_data.create(**row)

    try:
        service = MedicalInstitutionService()
        service.create(medical_institutions_data)
    except (DatabaseConnectionError, ServiceError, DataModelError) as e:
        logger.warning(e.message)
        return False

    logger.info("医療機関のデータ登録処理が完了しました。")
    return True


if __name__ == "__main__":
    import_hokkaido_data(Config.HOKKAIDO_URL)
    # 旭川市の陽性患者データをダウンロードしてデータベースへ登録
    download_lists = [
        (Config.NOV2020_OR_EARLIER_URL, 2020),
        (Config.DEC2020_DATA_URL, 2020),
        (Config.JAN2021_DATA_URL, 2021),
        (Config.FEB2021_DATA_URL, 2021),
        (Config.MAR2021_DATA_URL, 2021),
        (Config.APR2021_DATA_URL, 2021),
        (Config.MAY2021_DATA_URL, 2021),
        (Config.JUN2021_DATA_URL, 2021),
        (Config.JUL2021_DATA_URL, 2021),
        (Config.LATEST_DATA_URL, 2021),
    ]
    # import_asahikawa_data(download_lists)
    import_medical_institutions_data(Config.MEDICAL_INSTITUTIONS_URL)
