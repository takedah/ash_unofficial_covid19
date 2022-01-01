from datetime import date
from typing import Optional

from .config import Config
from .errors import DatabaseConnectionError, DataModelError, HTTPDownloadError, ScrapeError, ServiceError
from .models.patient import AsahikawaPatientFactory, HokkaidoPatientFactory
from .models.press_release_link import PressReleaseLinkFactory
from .models.sapporo_patients_number import SapporoPatientsNumberFactory
from .scrapers.patient import ScrapeAsahikawaPatients, ScrapeAsahikawaPatientsPDF, ScrapeHokkaidoPatients
from .scrapers.press_release_link import ScrapePressReleaseLink
from .scrapers.sapporo_patients_number import ScrapeSapporoPatientsNumber
from .services.patient import AsahikawaPatientService, HokkaidoPatientService
from .services.press_release_link import PressReleaseLinkService
from .services.sapporo_patients_number import SapporoPatientsNumberService


def _get_download_lists() -> list:
    """
    旭川市公式ホームページの前月分以前の感染者情報一覧のページURLをリストで返す。

    Returns:
        download_list (list of tuple): 前月分以前の感染者情報一覧のページのURLと対象年

    """
    return [
        (Config.NOV2020_OR_EARLIER_URL, 2020),
        (Config.DEC2020_DATA_URL, 2020),
        (Config.JAN2021_DATA_URL, 2021),
        (Config.FEB2021_DATA_URL, 2021),
        (Config.MAR2021_DATA_URL, 2021),
        (Config.APR2021_DATA_URL, 2021),
        (Config.MAY2021_DATA_URL, 2021),
        (Config.JUN2021_DATA_URL, 2021),
        (Config.JUL2021_DATA_URL, 2021),
        (Config.AUG2021_DATA_URL, 2021),
        (Config.SEP2021_DATA_URL, 2021),
        (Config.OCT2021_DATA_URL, 2021),
        (Config.NOV2021_DATA_URL, 2021),
        (Config.DEC2021_DATA_URL, 2021),
    ]


def _import_hokkaido_patients(url: str) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL

    """
    try:
        scraped_data = ScrapeHokkaidoPatients(url)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    patients_factory = HokkaidoPatientFactory()
    try:
        for row in scraped_data.lists:
            patients_factory.create(**row)
    except DataModelError as e:
        print(e.message)
        return

    service = HokkaidoPatientService()
    try:
        service.create(patients_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def _import_asahikawa_patients(url: str, target_year: int) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL
        target_year (int): 対象年

    """
    try:
        scraped_data = ScrapeAsahikawaPatients(html_url=url, target_year=target_year)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    patients_factory = AsahikawaPatientFactory()
    try:
        for row in scraped_data.lists:
            patients_factory.create(**row)
    except DataModelError as e:
        print(e.message)
        return

    service = AsahikawaPatientService()
    try:
        service.create(patients_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def _import_additional_asahikawa_patients() -> None:
    """HTMLに市内番号489の掲載が抜けているので手動で追加する"""
    patients_factory = AsahikawaPatientFactory()
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
        "occupation": "本市職員",
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
    try:
        service.create(patients_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def _import_press_release_link(url: str, target_year: int) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を、
    報道発表資料のPDFから抽出し、データベースへ格納するため、
    報道発表資料PDFファイル自体のURL等の情報を抽出する。

    Args:
        url (str): 旭川市公式ホームページのURL
        target_year (int): 対象年

    """
    try:
        scraped_data = ScrapePressReleaseLink(html_url=url, target_year=target_year)
    except (HTTPDownloadError, ScrapeError, DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return

    try:
        press_release_link_factory = PressReleaseLinkFactory()
        for row in scraped_data.lists:
            press_release_link_factory.create(**row)
    except DataModelError as e:
        print(e.message)
        return

    service = PressReleaseLinkService()
    try:
        service.create(press_release_link_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def _get_press_release_links() -> Optional[PressReleaseLinkFactory]:
    """報道発表資料PDFファイルのURLと報道発表日を要素に持つオブジェクトのリストを返す

    Returns:
        press_release_links (:obj:`PressReleaseLinkFactory`): 報道発表資料リスト
            報道発表資料PDFファイルのURLと報道発表日を要素に持つオブジェクトのリストを
            要素に持つオブジェクト

    """
    press_release_link_service = PressReleaseLinkService()
    try:
        return press_release_link_service.find_all()
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return None


def _import_asahikawa_data_from_press_release(pdf_url: str, publication_date: date) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を、
    報道発表資料のPDFから抽出し、データベースへ格納する。
    HTMLページの更新よりPDFファイルの更新の方が早いため、先にPDFからデータを抽出する。

    Args:
        url (str): 旭川市公式ホームページの報道発表資料PDFファイルのURL
        publication_date (int): 報道発表日

    """
    try:
        scraped_data = ScrapeAsahikawaPatientsPDF(pdf_url=pdf_url, publication_date=publication_date)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    service = AsahikawaPatientService()
    try:
        for row in scraped_data.lists:
            patients_factory = AsahikawaPatientFactory()
            patients_factory.create(**row)
            service.create(patients_factory)
    except (DatabaseConnectionError, ServiceError, DataModelError) as e:
        print(e.message)
        return


def _import_sapporo_patients_number(url: str) -> None:
    """DATA-SMART CITY SAPPOROから札幌市の1日の新規陽性患者数をインポートする

    Args:
        url (str): DATA-SMART CITY SAPPOROのCSVファイルのパス

    """
    try:
        scraped_data = ScrapeSapporoPatientsNumber(url)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    service = SapporoPatientsNumberService()
    sapporo_patients_number_factory = SapporoPatientsNumberFactory()
    for row in scraped_data.lists:
        sapporo_patients_number_factory.create(**row)

    try:
        service.create(sapporo_patients_number_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def import_latest():
    """今月の旭川市の新規陽性患者データを取得"""
    # 先にHTMLページから新規陽性患者データをデータベースへ登録
    _import_asahikawa_patients(url=Config.LATEST_DATA_URL, target_year=2022)

    # 最新の報道発表資料PDFファイルのURLと報道発表日をデータベースへ登録
    _import_press_release_link(Config.OVERVIEW_URL, 2022)

    # 最新の報道発表資料PDFファイルから新規陽性患者データをデータベースへ更新登録
    press_release_links = _get_press_release_links()
    if press_release_links:
        latest_press_release_link = press_release_links.items[0]
        _import_asahikawa_data_from_press_release(
            pdf_url=latest_press_release_link.url,
            publication_date=latest_press_release_link.publication_date,
        )

    # 札幌市の日別新規陽性患者数データをデータベースへ登録
    _import_sapporo_patients_number(Config.SAPPORO_URL)

    # 報道発表資料PDFファイルから新規陽性患者データをデータベースへ更新登録
    _import_press_release_link(url=Config.LATEST_DATA_URL, target_year=2022)
    press_release_links = _get_press_release_links()
    if press_release_links:
        for press_release_link in press_release_links.items:
            publication_date = press_release_link.publication_date
            if publication_date.year == 2022 and publication_date.month == 1:
                _import_asahikawa_data_from_press_release(
                    pdf_url=press_release_link.url,
                    publication_date=press_release_link.publication_date,
                )


def import_past():
    """先月以前の全ての新規陽性患者データを取得"""
    # 北海道の新規陽性患者データをデータベースへ登録
    _import_hokkaido_patients(Config.HOKKAIDO_URL)

    for download_list in _get_download_lists():
        url = download_list[0]
        target_year = download_list[1]
        # 先にHTMLページから新規陽性患者データをデータベースへ登録
        _import_asahikawa_patients(url=url, target_year=target_year)
        # 過去の報道発表資料PDFファイルのURLと報道発表日を取得
        _import_press_release_link(url=url, target_year=target_year)

    # 報道発表資料PDFファイルのURLと報道発表日を取得
    past_press_release_links = _get_press_release_links()
    if past_press_release_links:
        # 報道発表資料PDFファイルから新規陽性患者データをデータベースへ更新登録
        for press_release_link in past_press_release_links.items:
            _import_asahikawa_data_from_press_release(
                pdf_url=press_release_link.url,
                publication_date=press_release_link.publication_date,
            )

    _import_additional_asahikawa_patients()
    # 重複事例5例を削除する
    # https://www.pref.hokkaido.lg.jp/fs/4/0/4/0/0/1/8/_/hokkaido_z0519.pdf
    duplicate_patient_numbers = [7354, 9147, 9182, 11058, 30909]
    for patient_number in duplicate_patient_numbers:
        delete_patients(patient_number)


def delete_patients(patient_number: int):
    """
    指定した番号の新規陽性患者データを削除

    Args:
        patient_number (int): 削除したい番号

    """
    service = AsahikawaPatientService()
    try:
        service.delete(patient_number)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


if __name__ == "__main__":
    import_latest()
