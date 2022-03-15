from datetime import date

from .config import Config
from .errors import DatabaseConnectionError, HTTPDownloadError, ScrapeError, ServiceError
from .models.patients_number import PatientsNumberFactory
from .models.press_release_link import PressReleaseLinkFactory
from .models.sapporo_patients_number import SapporoPatientsNumberFactory
from .scrapers.patients_number import ScrapePatientsNumber
from .scrapers.press_release_link import ScrapePressReleaseLink
from .scrapers.sapporo_patients_number import ScrapeSapporoPatientsNumber
from .services.patient import AsahikawaPatientService
from .services.patients_number import PatientsNumberService
from .services.press_release_link import PressReleaseLinkService
from .services.sapporo_patients_number import SapporoPatientsNumberService


def _import_press_release_link(url: str, target_year: int) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の感染者情報を報道発表資料の
    PDFから抽出しデータベースへ格納するため、報道発表資料PDFファイル自体のURL等の
    情報を抽出する。

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
        factory = PressReleaseLinkFactory()
        for row in scraped_data.lists:
            factory.create(**row)
    except TypeError as e:
        print(e.args[0])
        return

    service = PressReleaseLinkService()
    try:
        service.create(factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def _get_press_release_links() -> PressReleaseLinkFactory:
    """報道発表資料PDFファイルのURLと報道発表日を要素に持つオブジェクトのリストを返す

    Returns:
        press_release_links (:obj:`PressReleaseLinkFactory`): 報道発表資料リスト
            報道発表資料PDFファイルのURLと報道発表日を要素に持つオブジェクトのリストを
            要素に持つオブジェクト

    """
    press_release_link_service = PressReleaseLinkService()
    return press_release_link_service.find_all()


def _import_asahikawa_data_from_press_release(pdf_url: str, publication_date: date) -> None:
    """
    旭川市公式ホームページから新型コロナウイルス感染症の新規陽性患者数を
    報道発表資料のPDFから抽出し、データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページの報道発表資料PDFファイルのURL
        publication_date (int): 報道発表日

    """
    try:
        scraped_data = ScrapePatientsNumber(pdf_url=pdf_url, publication_date=publication_date)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    factory = PatientsNumberFactory()
    try:
        for row in scraped_data.lists:
            factory.create(**row)
    except TypeError as e:
        print(e.args[0])
        return

    try:
        service = PatientsNumberService()
        service.create(factory)
    except (DatabaseConnectionError, ServiceError) as e:
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
    factory = SapporoPatientsNumberFactory()
    for row in scraped_data.lists:
        factory.create(**row)

    try:
        service.create(factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def _fix_asahikawa_data() -> None:
    """
    報道発表資料に後日訂正があった分のデータを修正する。

    """
    factory = PatientsNumberFactory()

    # 令和4年2月20日発表分の訂正
    # 発表資料ではどの年代を1名取り下げたのか不明なため、調査中から1名減とした。
    # https://www.city.asahikawa.hokkaido.jp/kurashi/135/136/150/d074697_d/fil/0220-2.pdf
    fix_20220220 = {
        "publication_date": date(2022, 2, 20),
        "age_under_10": 24,
        "age_10s": 13,
        "age_20s": 12,
        "age_30s": 10,
        "age_40s": 8,
        "age_50s": 7,
        "age_60s": 7,
        "age_70s": 8,
        "age_80s": 3,
        "age_over_90": 5,
        "investigating": 0,
    }
    factory.create(**fix_20220220)

    try:
        service = PatientsNumberService()
        service.create(factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


def import_latest():
    # 最新の報道発表資料PDFファイルのURLと報道発表日をデータベースへ登録
    _import_press_release_link(Config.OVERVIEW_URL, 2022)

    # 最新の報道発表資料PDFファイルから年代別新規陽性患者数データをデータベースへ登録
    press_release_links = _get_press_release_links()
    latest_press_release_link = press_release_links.items[0]
    _import_asahikawa_data_from_press_release(
        pdf_url=latest_press_release_link.url,
        publication_date=latest_press_release_link.publication_date,
    )

    # 今月の報道発表資料PDFファイルから日別年代別陽性患者数データをデータベースへ登録
    _import_press_release_link(url=Config.LATEST_DATA_URL, target_year=2022)
    press_release_links = _get_press_release_links()
    for press_release_link in press_release_links.items:
        publication_date = press_release_link.publication_date
        if date(2022, 1, 27) < publication_date:
            if publication_date.year == 2022 and publication_date.month == 3:
                _import_asahikawa_data_from_press_release(
                    pdf_url=press_release_link.url,
                    publication_date=press_release_link.publication_date,
                )

    # 札幌市の日別新規陽性患者数データをデータベースへ登録
    _import_sapporo_patients_number(Config.SAPPORO_URL)


def import_past_from_patients():
    # 過去の陽性患者属性データベースから日別年代別陽性患者数データをデータベースへ登録
    service = AsahikawaPatientService()
    factory = PatientsNumberFactory()
    try:
        for row in service.get_aggregate_by_days_per_age(date(2020, 2, 23), date(2022, 1, 27)):
            factory.create(**row)
    except TypeError as e:
        print(e.args[0])
        return

    try:
        service = PatientsNumberService()
        service.create(factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)
        return


if __name__ == "__main__":
    import_latest()
