from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.errors import (
    DatabaseError,
    DataError,
    DataModelError,
    HTTPDownloadError
)
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.models import PatientFactory
from ash_unofficial_covid19.scraper import DownloadedHTML, ScrapedHTMLData
from ash_unofficial_covid19.services import PatientService


def import_asahikawa_data(url: str, target_year: int):
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
    patients_data = PatientFactory()
    for row in scraped_data.patients_data:
        patients_data.create(**row)

    try:
        conn = DB()
        service = PatientService(conn)
        for patient in patients_data.items:
            service.create(patient)
        conn.commit()
        conn.close()
    except (DataError, DatabaseError, DataModelError) as e:
        conn.close()
        logger.warning(e.message)
        return False

    logger.info("処理が完了しました。")


if __name__ == "__main__":
    import_asahikawa_data(Config.NOV2020_OR_EARLIER_URL, 2020)
