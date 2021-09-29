import unittest

from ash_unofficial_covid19.errors import ServiceError
from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.medical_institution import MedicalInstitutionFactory
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.medical_institution import (
    MedicalInstitutionService,
)
from ash_unofficial_covid19.services.medical_institution_location import (
    MedicalInstitutionLocationService,
)


class TestMedicalInstitutionLocationService(unittest.TestCase):
    def setUp(self):
        # 医療機関データのセットアップ
        test_medical_institutions_data = [
            {
                "name": "市立旭川病院",
                "address": "旭川市金星町1",
                "phone_number": "0166-29-0202",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "新富・東・金星町",
                "memo": "",
                "target_age": "16歳以上",
            },
            {
                "name": "道北勤医協一条通病院",
                "address": "旭川市東光1の1",
                "phone_number": "0166-34-0015 予約専用",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "大成",
                "memo": (
                    "道北勤医協一条通病院及び道北勤医協一条クリニックは、"
                    + "予約専用番号(34-0015)に変更となります。 開始時期は、"
                    + "各医療機関のホームページ及び院内掲示をご覧ください。"
                ),
                "target_age": "16歳以上",
            },
            {
                "name": "市立旭川病院",
                "address": "旭川市金星町1",
                "phone_number": "0166-29-0202",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "東・金星町・各条17〜26丁目",
                "memo": "",
                "target_age": "12歳から15歳まで",
            },
            {
                "name": "独立行政法人国立病院機構旭川医療センター",
                "address": "旭川市花咲町7",
                "phone_number": "0166-51-3910 予約専用",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "花咲町・末広・末広東・永山",
                "memo": "",
                "target_age": "12歳から15歳まで",
            },
        ]
        medical_institution_factory = MedicalInstitutionFactory()
        for row in test_medical_institutions_data:
            medical_institution_factory.create(**row)
        medical_institution_service = MedicalInstitutionService()
        medical_institution_service.create(medical_institution_factory)

        # 位置情報データのセットアップ
        test_locations_data = [
            {
                "medical_institution_name": "市立旭川病院",
                "longitude": 142.365976388889,
                "latitude": 43.778422777778,
            },
        ]
        location_factory = LocationFactory()
        for row in test_locations_data:
            location_factory.create(**row)
        location_service = LocationService()
        location_service.create(location_factory)

        self.service = MedicalInstitutionLocationService()

    def test_find(self):
        # 対象年齢を指定しない場合16歳以上の医療機関を返す
        result = self.service.find(name="市立旭川病院")
        self.assertEqual(result.name, "市立旭川病院")
        self.assertEqual(result.address, "旭川市金星町1")
        self.assertEqual(result.phone_number, "0166-29-0202")
        self.assertEqual(result.book_at_medical_institution, True)
        self.assertEqual(result.book_at_call_center, False)
        self.assertEqual(result.area, "新富・東・金星町")
        self.assertEqual(result.memo, "")
        self.assertEqual(result.target_age, "16歳以上")
        self.assertEqual(result.latitude, 43.778422777778)
        self.assertEqual(result.longitude, 142.365976388889)

        # 対象年齢を指定する場合
        result = self.service.find(name="市立旭川病院", is_pediatric=True)
        self.assertEqual(result.name, "市立旭川病院")
        self.assertEqual(result.address, "旭川市金星町1")
        self.assertEqual(result.phone_number, "0166-29-0202")
        self.assertEqual(result.book_at_medical_institution, True)
        self.assertEqual(result.book_at_call_center, False)
        self.assertEqual(result.area, "東・金星町・各条17〜26丁目")
        self.assertEqual(result.memo, "")
        self.assertEqual(result.target_age, "12歳から15歳まで")
        self.assertEqual(result.latitude, 43.778422777778)
        self.assertEqual(result.longitude, 142.365976388889)

        # 存在しない医療機関名を指定
        with self.assertRaises(ServiceError):
            self.service.find(name="hoge")

    def test_find_area(self):
        # 対象年齢を指定しない場合16歳以上の医療機関を返す
        results = self.service.find_area(area="新富・東・金星町")
        result = results.items[0]
        self.assertEqual(result.name, "市立旭川病院")
        self.assertEqual(result.address, "旭川市金星町1")
        self.assertEqual(result.phone_number, "0166-29-0202")
        self.assertEqual(result.book_at_medical_institution, True)
        self.assertEqual(result.book_at_call_center, False)
        self.assertEqual(result.area, "新富・東・金星町")
        self.assertEqual(result.memo, "")
        self.assertEqual(result.target_age, "16歳以上")
        self.assertEqual(result.latitude, 43.778422777778)
        self.assertEqual(result.longitude, 142.365976388889)

        # 対象年齢を指定する場合
        results = self.service.find_area(area="東・金星町・各条17〜26丁目", is_pediatric=True)
        result = results.items[0]
        self.assertEqual(result.name, "市立旭川病院")
        self.assertEqual(result.address, "旭川市金星町1")
        self.assertEqual(result.phone_number, "0166-29-0202")
        self.assertEqual(result.book_at_medical_institution, True)
        self.assertEqual(result.book_at_call_center, False)
        self.assertEqual(result.area, "東・金星町・各条17〜26丁目")
        self.assertEqual(result.memo, "")
        self.assertEqual(result.target_age, "12歳から15歳まで")
        self.assertEqual(result.latitude, 43.778422777778)
        self.assertEqual(result.longitude, 142.365976388889)

        # 存在しない地域を指定
        with self.assertRaises(ServiceError):
            self.service.find_area(area="fuga")


if __name__ == "__main__":
    unittest.main()
