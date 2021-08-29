from datetime import date

from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.errors import HTTPDownloadError
from ash_unofficial_covid19.models.patient import (
    AsahikawaPatientFactory,
    HokkaidoPatientFactory
)
from ash_unofficial_covid19.models.press_release_link import (
    PressReleaseLinkFactory
)
from ash_unofficial_covid19.scrapers.patient import (
    ScrapeAsahikawaPatients,
    ScrapeAsahikawaPatientsPDF,
    ScrapeHokkaidoPatients
)
from ash_unofficial_covid19.scrapers.press_release_link import (
    ScrapePressReleaseLink
)
from ash_unofficial_covid19.services.patient import (
    AsahikawaPatientService,
    HokkaidoPatientService
)
from ash_unofficial_covid19.services.press_release_link import (
    PressReleaseLinkService
)


def import_hokkaido_patients(url: str) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL

    """
    scraped_data = ScrapeHokkaidoPatients(url)
    patients_factory = HokkaidoPatientFactory()
    for row in scraped_data.lists:
        patients_factory.create(**row)

    service = HokkaidoPatientService()
    service.create(patients_factory)


def import_asahikawa_patients(download_lists: list) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を、
    データベースへ格納する。

    Args:
        download_lists (list of tuple): スクレイピング対象URLとデータの対象年を要素に
            持つタプルを要素としたリスト

    """
    patients_factory = AsahikawaPatientFactory()
    for download_list in download_lists:
        url = download_list[0]
        target_year = download_list[1]
        try:
            scraped_data = ScrapeAsahikawaPatients(
                html_url=url, target_year=target_year
            )
        except HTTPDownloadError:
            continue
        for row in scraped_data.lists:
            patients_factory.create(**row)

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
    patients_factory.create(**additional_data)

    service = AsahikawaPatientService()
    service.create(patients_factory)


def _import_press_release_link(url: str, target_year: int) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を、
    報道発表資料のPDFから抽出し、データベースへ格納するため、
    報道発表資料PDFファイル自体のURL等の情報を抽出する。

    Args:
        url (str): 旭川市公式ホームページのURL
        target_year (int): 対象年

    """
    scraped_data = ScrapePressReleaseLink(html_url=url, target_year=target_year)
    press_release_link_factory = PressReleaseLinkFactory()
    for row in scraped_data.lists:
        press_release_link_factory.create(**row)

    service = PressReleaseLinkService()
    service.create(press_release_link_factory)


def import_asahikawa_data_from_press_release(url: str, target_year: int) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を、
    報道発表資料のPDFから抽出し、データベースへ格納する。
    HTMLページの更新よりPDFファイルの更新の方が早いため、先にPDFからデータを抽出する。

    Args:
        url (str): 旭川市公式ホームページのURL
        target_year (int): 対象年

    """
    _import_press_release_link(url, target_year)
    press_release_link_service = PressReleaseLinkService()
    press_release_links = press_release_link_service.find_all()
    latest_press_release_link = press_release_links.items[0]
    publication_date = latest_press_release_link.publication_date
    pdf_url = latest_press_release_link.url

    scraped_data = ScrapeAsahikawaPatientsPDF(
        pdf_url=pdf_url, publication_date=publication_date
    )
    service = AsahikawaPatientService()
    for row in scraped_data.lists:
        patients_factory = AsahikawaPatientFactory()
        patients_factory.create(**row)
        service.create(patients_factory)


if __name__ == "__main__":
    import_asahikawa_data_from_press_release(Config.OVERVIEW_URL, 2021)
    # import_hokkaido_patients(Config.HOKKAIDO_URL)
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
    import_asahikawa_patients(download_lists)
