import time

from .config import Config
from .errors import DatabaseConnectionError, HTTPDownloadError, ScrapeError, ServiceError
from .models.location import LocationFactory
from .models.medical_institution import MedicalInstitutionFactory
from .scrapers.location import ScrapeYOLPLocation
from .scrapers.medical_institution import ScrapeMedicalInstitutions
from .services.location import LocationService
from .services.medical_institution import MedicalInstitutionService


def import_medical_institutions(url: str) -> None:
    """
    旭川市公式ホームページから新型コロナワクチン接種医療機関一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL

    """
    medical_institution_factory = MedicalInstitutionFactory()

    # 16歳以上
    try:
        scraped_data = ScrapeMedicalInstitutions(html_url=url)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    for row in scraped_data.lists:
        medical_institution_factory.create(**row)

    # 12歳から15歳まで
    try:
        scraped_pediatric_data = ScrapeMedicalInstitutions(html_url=url, is_pediatric=True)
    except (HTTPDownloadError, ScrapeError) as e:
        print(e.message)
        return

    for row in scraped_pediatric_data.lists:
        medical_institution_factory.create(**row)

    service = MedicalInstitutionService()
    try:
        current_name_list = service.get_name_lists()
        new_name_list = scraped_data.get_name_lists()
        new_name_list.extend(scraped_pediatric_data.get_name_lists())
        added_names = list(set(new_name_list) - set(current_name_list))
        service.create(medical_institution_factory)
        updated_name_list = service.get_name_lists()
        non_exist_names = list(set(updated_name_list) - set(new_name_list))
        for non_exist_name in non_exist_names:
            service.delete(non_exist_name)

        import_locations(added_names)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)

    return


def import_locations(medical_institution_name_list: list) -> None:
    """
    医療機関の名称一覧から緯度経度を取得し、データベースへ格納する。

    Args:
        name_list (list): 医療機関名のリスト

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

    service = LocationService()
    try:
        service.create(locations_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)

    # YOLPで緯度経度を取得できなかった医療機関に手動で情報を追加
    fix_data = [
        {
            "medical_institution_name": "唐沢病院",
            "longitude": 142.36361116952028,
            "latitude": 43.76824898808485,
        },
        {
            "medical_institution_name": "旭川キュアメディクス",
            "longitude": 142.37285062533863,
            "latitude": 43.76773531393752,
        },
        {
            "medical_institution_name": "豊岡産科婦人科医院",
            "longitude": 142.3898197271928,
            "latitude": 43.760557864278475,
        },
        {
            "medical_institution_name": "佐藤内科医院",
            "longitude": 142.39588151965012,
            "latitude": 43.76034860571178,
        },
        {
            "medical_institution_name": "東旭川病院",
            "longitude": 142.4377094983569,
            "latitude": 43.777870139580855,
        },
        {
            "medical_institution_name": "フクダクリニック",
            "longitude": 142.38243298115825,
            "latitude": 43.81521459576975,
        },
        {
            "medical_institution_name": "旭川リハビリテーション病院",
            "longitude": 142.3871075983558,
            "latitude": 43.73051097382853,
        },
        {
            "medical_institution_name": "旭川医科大学病院",
            "longitude": 142.38382199835564,
            "latitude": 43.73007572101459,
        },
        {
            "medical_institution_name": "小児科くさのこどもクリニック",
            "longitude": 142.39032599835747,
            "latitude": 43.80567852167143,
        },
        {
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "longitude": 142.3815237271935,
            "latitude": 43.798826491523464,
        },
    ]
    locations_factory = LocationFactory()
    for row in fix_data:
        locations_factory.create(**row)

    try:
        service.create(locations_factory)
    except (DatabaseConnectionError, ServiceError) as e:
        print(e.message)

    return


if __name__ == "__main__":
    import_medical_institutions(Config.MEDICAL_INSTITUTIONS_URL)
