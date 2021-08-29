import unittest

from ash_unofficial_covid19.models.medical_institution import (
    MedicalInstitutionFactory
)
from ash_unofficial_covid19.services.medical_institution import (
    MedicalInstitutionService
)


class TestMedicalInstitutionService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
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
        self.factory = MedicalInstitutionFactory()
        for row in test_data:
            self.factory.create(**row)
        self.service = MedicalInstitutionService()
        self.service.create(self.factory)

    def test_find_all(self):
        results = self.service.find_all()
        medical_institution = results.items[0]
        self.assertEqual(medical_institution.name, "市立旭川病院")
        self.assertEqual(medical_institution.book_at_medical_institution, True)
        self.assertEqual(medical_institution.book_at_call_center, False)

    def test_get_csv_rows(self):
        results = self.service.get_csv_rows()
        expect = [
            [
                "地区",
                "医療機関名",
                "住所",
                "電話",
                "かかりつけの医療機関で予約ができます",
                "コールセンターやインターネットで予約ができます",
                "対象年齢",
                "備考",
            ],
            [
                "新富・東・金星町",
                "市立旭川病院",
                "旭川市金星町1",
                "0166-29-0202",
                "1",
                "0",
                "16歳以上",
                "",
            ],
            [
                "大成",
                "道北勤医協一条通病院",
                "旭川市東光1の1",
                "0166-34-0015 予約専用",
                "1",
                "0",
                "16歳以上",
                (
                    "道北勤医協一条通病院及び道北勤医協一条クリニックは、"
                    + "予約専用番号(34-0015)に変更となります。 開始時期は、"
                    + "各医療機関のホームページ及び院内掲示をご覧ください。"
                ),
            ],
            [
                "東・金星町・各条17〜26丁目",
                "市立旭川病院",
                "旭川市金星町1",
                "0166-29-0202",
                "1",
                "0",
                "12歳から15歳まで",
                "",
            ],
            [
                "花咲町・末広・末広東・永山",
                "独立行政法人国立病院機構旭川医療センター",
                "旭川市花咲町7",
                "0166-51-3910 予約専用",
                "1",
                "0",
                "12歳から15歳まで",
                "",
            ],
        ]
        self.assertEqual(results, expect)

    def test_get_name_list(self):
        results = self.service.get_name_list()
        expect = ["市立旭川病院", "道北勤医協一条通病院", "独立行政法人国立病院機構旭川医療センター"]
        self.assertEqual(results, expect)

    def test_get_area_list(self):
        # 対象年齢を指定しない場合16歳以上の医療機関を返す
        results = self.service.get_area_list()
        expect = ["新富・東・金星町", "大成"]
        self.assertEqual(results, expect)

        # 対象年齢を指定する場合
        results = self.service.get_area_list(is_pediatric=True)
        expect = ["花咲町・末広・末広東・永山", "東・金星町・各条17〜26丁目"]
        self.assertEqual(results, expect)

    def test_get_locations(self):
        # 対象年齢を指定しない場合16歳以上の医療機関を返す
        results = self.service.get_locations(area="新富・東・金星町")
        expect = [
            (
                "市立旭川病院",
                "旭川市金星町1",
                "0166-29-0202",
                True,
                False,
                "",
                43.778422777778,
                142.365976388889,
            )
        ]
        self.assertEqual(results, expect)

        # 対象年齢を指定する場合
        results = self.service.get_locations(area="東・金星町・各条17〜26丁目", is_pediatric=True)
        expect = [
            (
                "市立旭川病院",
                "旭川市金星町1",
                "0166-29-0202",
                True,
                False,
                "",
                43.778422777778,
                142.365976388889,
            )
        ]
        self.assertEqual(results, expect)


if __name__ == "__main__":
    unittest.main()
