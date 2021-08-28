import time

from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.medical_institution import (
    MedicalInstitutionFactory
)
from ash_unofficial_covid19.scrapers.downloader import DownloadedHTML
from ash_unofficial_covid19.scrapers.location import ScrapeYOLPLocation
from ash_unofficial_covid19.scrapers.medical_institution import (
    ScrapeMedicalInstitutions
)
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.medical_institution import (
    MedicalInstitutionService
)


def import_medical_institutions_data(url: str) -> None:
    """
    旭川市公式ホームページから新型コロナワクチン接種医療機関一覧を取得し、
    データベースへ格納する。

    Args:
        url (str): 旭川市公式ホームページのURL

    """
    html_content = DownloadedHTML(url)
    scraped_data = ScrapeMedicalInstitutions(html_content)
    medical_institutions_data = MedicalInstitutionFactory()
    for row in scraped_data.lists:
        medical_institutions_data.create(**row)

    service = MedicalInstitutionService()
    service.create(medical_institutions_data)


def import_locations_data() -> None:
    """
    医療機関の名称一覧から緯度経度を取得し、データベースへ格納する。

    """
    medical_institution_service = MedicalInstitutionService()
    medical_institution_names = medical_institution_service.get_name_list()

    locations_data = LocationFactory()
    for medical_institution_name in medical_institution_names:
        scraped_data = ScrapeYOLPLocation(medical_institution_name)
        # 1番目の検索結果を採用する
        row = scraped_data.lists[0]
        locations_data.create(**row)
        time.sleep(1)

    service = LocationService()
    service.create(locations_data)

    # YOLPで緯度経度を取得できなかった医療機関に手動で情報を追加
    fix_list = [
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
            "medical_institution_name": "旭川医療センター",
            "longitude": 142.3815237271935,
            "latitude": 43.798826491523464,
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
    ]
    locations_data = LocationFactory()
    for row in fix_list:
        locations_data.create(**row)
    service.create(locations_data)


if __name__ == "__main__":
    import_medical_institutions_data(Config.MEDICAL_INSTITUTIONS_URL)
    import_locations_data()
