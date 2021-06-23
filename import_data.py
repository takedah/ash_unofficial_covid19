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
    DownloadedHTML,
    DownloadedPDF,
    ScrapedCSVData,
    ScrapedHTMLData,
    ScrapedPDFData
)
from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    HokkaidoPatientService,
    MedicalInstitutionService
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
        service = HokkaidoPatientService()
        service.create(patients_data)
    except (DatabaseConnectionError, ServiceError, DataModelError) as e:
        logger.warning(e.message)
        return False

    logger.info("北海道のデータ登録処理が完了しました。")
    return True


def get_asahikawa_data(url: str, target_year: int) -> ScrapedHTMLData:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報一覧を取得する。

    Args:
        url (str): 旭川市公式ホームページのURL
        target_year (int): 対象年

    Returns:
        scraped_data (obj:`ScrapedHTMLData`): ダウンロードしたHTMLデータ

    """
    logger = AppLog()
    try:
        html_data = DownloadedHTML(url)
    except HTTPDownloadError as e:
        logger.warning(e.message)
        return False

    scraped_data = ScrapedHTMLData(downloaded_html=html_data, target_year=target_year)
    return scraped_data


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
    logger = AppLog()
    patients_data = AsahikawaPatientFactory()
    for download_list in download_lists:
        url = download_list[0]
        target_year = download_list[1]
        scraped_data = get_asahikawa_data(url=url, target_year=target_year)
        for row in scraped_data.patients_data:
            patients_data.create(**row)
    try:
        service = AsahikawaPatientService()
        service.create(patients_data)
    except (DatabaseConnectionError, ServiceError, DataModelError) as e:
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
        service = AsahikawaPatientService()
        for duplicate_patient_number in service.get_duplicate_patient_numbers():
            service.delete(patient_number=duplicate_patient_number)
    except (DatabaseConnectionError, ServiceError) as e:
        logger.warning(e.message)
        return False

    logger.info("重複事例のデータ削除処理が完了しました。")
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
    logger = AppLog()
    try:
        pdf_content = DownloadedPDF(url)
    except HTTPDownloadError as e:
        logger.warning(e.message)
        return False

    scraped_data = ScrapedPDFData(pdf_content)
    medical_institutions_data = MedicalInstitutionFactory()
    for row in scraped_data.medical_institutions_data:
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
    # 北海道の陽性患者データをデータベースへ登録
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
        (Config.LATEST_DATA_URL, 2021),
    ]
    import_asahikawa_data(download_lists)
    delete_duplicate_data()

    # 旭川市のワクチン接種医療機関の一覧をデータベースへ登録
    import_medical_institutions_data(Config.PDF_URL)
