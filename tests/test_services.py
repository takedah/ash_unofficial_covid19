import unittest
from datetime import date

import pandas as pd
from pandas._testing import assert_frame_equal

from ash_unofficial_covid19.errors import ServiceError
from ash_unofficial_covid19.models import (
    AsahikawaPatientFactory,
    HokkaidoPatientFactory,
    LocationFactory,
    MedicalInstitutionFactory,
    PressReleaseLinkFactory
)
from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    HokkaidoPatientService,
    LocationService,
    MedicalInstitutionService,
    PressReleaseLinkService
)


class TestAsahikawaPatientService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
            {
                "patient_number": 1121,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 27),
                "onset_date": None,
                "residence": "旭川市",
                "age": "30代",
                "sex": "男性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 1 周囲の患者の発生: "
                + "No.1072 No.1094 No.1107 No.1108 濃厚接触者の状況: 0人",
                "hokkaido_patient_number": 1,
                "surrounding_status": "No.1072 No.1094 No.1107 No.1108",
                "close_contact": "0人",
            },
            {
                "patient_number": 1120,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 26),
                "onset_date": None,
                "residence": "旭川市",
                "age": "50代",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 2 周囲の患者の発生: 調査中 濃厚接触者の状況: 2人",
                "hokkaido_patient_number": 2,
                "surrounding_status": "調査中",
                "close_contact": "2人",
            },
            {
                "patient_number": 1119,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 25),
                "onset_date": None,
                "residence": "旭川市",
                "age": "",
                "sex": "",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 3 周囲の患者の発生: No.1092             "
                + "No.1093 濃厚接触者の状況: 1人",
                "hokkaido_patient_number": 3,
                "surrounding_status": "No.1092             No.1093",
                "close_contact": "1人",
            },
            {
                "patient_number": 1112,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 22),
                "onset_date": None,
                "residence": "旭川市",
                "age": "10歳未満",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 18891 周囲の患者の発生: No.1074 濃厚接触者の状況: 0人",
                "hokkaido_patient_number": 18891,
                "surrounding_status": "No.1074",
                "close_contact": "0人",
            },
            {
                "patient_number": 1032,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 1, 31),
                "onset_date": None,
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "男性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 17511 周囲の患者の発生: 調査中 濃厚接触者の状況: 8人",
                "hokkaido_patient_number": 17511,
                "surrounding_status": "調査中",
                "close_contact": "8人",
            },
            {
                "patient_number": 715,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 12, 9),
                "onset_date": None,
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 10716 周囲の患者の発生: あり 濃厚接触者の状況: 調査中",
                "hokkaido_patient_number": 10716,
                "surrounding_status": "あり",
                "close_contact": "調査中",
            },
        ]
        self.factory = AsahikawaPatientFactory()
        for row in test_data:
            self.factory.create(**row)
        self.service = AsahikawaPatientService()
        self.service.create(self.factory)

        # 北海道の新型コロナウイルス感染症患者データのセットアップ
        test_hokkaido_data = [
            {
                "patient_number": 1,
                "city_code": "10006",
                "prefecture": "北海道",
                "city_name": "",
                "publication_date": date(2020, 1, 28),
                "onset_date": date(2020, 1, 21),
                "residence": "中国武漢市",
                "age": "40代",
                "sex": "女性",
                "occupation": "－",
                "status": "－",
                "symptom": "発熱",
                "overseas_travel_history": True,
                "be_discharged": None,
                "note": "海外渡航先：中国武漢",
            },
            {
                "patient_number": 2,
                "city_code": "10006",
                "prefecture": "北海道",
                "city_name": "",
                "publication_date": date(2020, 2, 14),
                "onset_date": date(2020, 1, 31),
                "residence": "重複削除",
                "age": "50代",
                "sex": "男性",
                "occupation": "自営業",
                "status": "－",
                "symptom": "発熱;咳;倦怠感",
                "overseas_travel_history": False,
                "be_discharged": None,
                "note": "",
            },
            {
                "patient_number": 3,
                "city_code": "10006",
                "prefecture": "北海道",
                "city_name": "",
                "publication_date": date(2020, 2, 19),
                "onset_date": date(2020, 2, 8),
                "residence": "石狩振興局管内",
                "age": "40代",
                "sex": "男性",
                "occupation": "会社員",
                "status": "－",
                "symptom": "倦怠感;筋肉痛;関節痛;発熱;咳",
                "overseas_travel_history": False,
                "be_discharged": None,
                "note": "",
            },
        ]
        self.hokkaido_factory = HokkaidoPatientFactory()
        for row in test_hokkaido_data:
            self.hokkaido_factory.create(**row)
        self.hokkaido_service = HokkaidoPatientService()
        self.hokkaido_service.create(self.hokkaido_factory)

    def test_delete(self):
        self.assertTrue(self.service.delete(patient_number=1121))

    def test_find_all(self):
        results = self.service.find_all()
        patient = results.items[0]
        self.assertEqual(patient.patient_number, 715)
        self.assertEqual(patient.publication_date, date(2021, 12, 9))
        self.assertEqual(patient.age, "90歳以上")
        self.assertEqual(patient.sex, "女性")

    def test_find(self):
        results = self.service.find(page=1, desc=False)
        patient = results[0].items[1]
        self.assertEqual(patient.patient_number, 1032)
        # 存在しないページ指定
        with self.assertRaises(ServiceError):
            self.service.find(page=2)

    def test_get_csv_rows(self):
        results = self.service.get_csv_rows()
        expect = [
            [
                "No",
                "全国地方公共団体コード",
                "都道府県名",
                "市区町村名",
                "公表_年月日",
                "発症_年月日",
                "患者_居住地",
                "患者_年代",
                "患者_性別",
                "患者_職業",
                "患者_状態",
                "患者_症状",
                "患者_渡航歴の有無フラグ",
                "患者_退院済フラグ",
                "備考",
            ],
            [
                "715",
                "012041",
                "北海道",
                "旭川市",
                "2021-12-09",
                "",
                "旭川市",
                "90歳以上",
                "女性",
                "",
                "",
                "",
                "",
                "",
                "北海道発表NO.: 10716 周囲の患者の発生: あり 濃厚接触者の状況: 調査中",
            ],
            [
                "1032",
                "012041",
                "北海道",
                "旭川市",
                "2021-01-31",
                "",
                "旭川市",
                "90歳以上",
                "男性",
                "",
                "",
                "",
                "",
                "",
                "北海道発表NO.: 17511 周囲の患者の発生: 調査中 濃厚接触者の状況: 8人",
            ],
            [
                "1112",
                "012041",
                "北海道",
                "旭川市",
                "2021-02-22",
                "",
                "旭川市",
                "10歳未満",
                "女性",
                "",
                "",
                "",
                "",
                "",
                "北海道発表NO.: 18891 周囲の患者の発生: No.1074 濃厚接触者の状況: 0人",
            ],
            [
                "1119",
                "012041",
                "北海道",
                "旭川市",
                "2021-02-25",
                "2020-02-08",
                "旭川市",
                "",
                "",
                "会社員",
                "－",
                "倦怠感;筋肉痛;関節痛;発熱;咳",
                "0",
                "",
                "北海道発表NO.: 3 周囲の患者の発生: No.1092             " + "No.1093 濃厚接触者の状況: 1人",
            ],
            [
                "1120",
                "012041",
                "北海道",
                "旭川市",
                "2021-02-26",
                "2020-01-31",
                "旭川市",
                "50代",
                "女性",
                "自営業",
                "－",
                "発熱;咳;倦怠感",
                "0",
                "",
                "北海道発表NO.: 2 周囲の患者の発生: 調査中 濃厚接触者の状況: 2人",
            ],
            [
                "1121",
                "012041",
                "北海道",
                "旭川市",
                "2021-02-27",
                "2020-01-21",
                "旭川市",
                "30代",
                "男性",
                "－",
                "－",
                "発熱",
                "1",
                "",
                "北海道発表NO.: 1 周囲の患者の発生: "
                + "No.1072 No.1094 No.1107 No.1108 濃厚接触者の状況: 0人",
            ],
        ]
        self.assertEqual(results, expect)

    def test_get_aggregate_by_days(self):
        from_date = date(2021, 2, 22)
        to_date = date(2021, 2, 28)
        result = self.service.get_aggregate_by_days(
            from_date=from_date, to_date=to_date
        )
        expect = [
            (date(2021, 2, 22), 1),
            (date(2021, 2, 23), 0),
            (date(2021, 2, 24), 0),
            (date(2021, 2, 25), 1),
            (date(2021, 2, 26), 1),
            (date(2021, 2, 27), 1),
            (date(2021, 2, 28), 0),
        ]
        self.assertEqual(result, expect)

    def test_get_aggregate_by_weeks(self):
        from_date = date(2021, 1, 25)
        to_date = date(2021, 2, 28)
        result = self.service.get_aggregate_by_weeks(
            from_date=from_date, to_date=to_date
        )
        expect = [
            (date(2021, 1, 25), 1),
            (date(2021, 2, 1), 0),
            (date(2021, 2, 8), 0),
            (date(2021, 2, 15), 0),
            (date(2021, 2, 22), 4),
        ]
        self.assertEqual(result, expect)

    def test_get_aggregate_by_weeks_per_age(self):
        from_date = date(2021, 1, 25)
        to_date = date(2021, 2, 28)
        result = self.service.get_aggregate_by_weeks_per_age(
            from_date=from_date, to_date=to_date
        )
        expect = pd.DataFrame(
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
            ],
            columns=[
                "10歳未満",
                "10代",
                "20代",
                "30代",
                "40代",
                "50代",
                "60代",
                "70代",
                "80代",
                "90歳以上",
                "非公表",
            ],
            index=[
                date(2021, 1, 25),
                date(2021, 2, 1),
                date(2021, 2, 8),
                date(2021, 2, 15),
                date(2021, 2, 22),
            ],
        )
        assert_frame_equal(result, expect)

    def test_get_seven_days_moving_average(self):
        from_date = date(2021, 1, 25)
        to_date = date(2021, 2, 28)
        result = self.service.get_seven_days_moving_average(
            from_date=from_date, to_date=to_date
        )
        expect = [
            (date(2021, 1, 25), 0.14),
            (date(2021, 2, 1), 0),
            (date(2021, 2, 8), 0),
            (date(2021, 2, 15), 0),
            (date(2021, 2, 22), 0.57),
        ]
        self.assertEqual(result, expect)

    def test_get_per_hundred_thousand_population_per_week(self):
        from_date = date(2021, 1, 25)
        to_date = date(2021, 2, 28)
        result = self.service.get_per_hundred_thousand_population_per_week(
            from_date=from_date, to_date=to_date
        )
        expect = [
            (date(2021, 1, 25), 0.30),
            (date(2021, 2, 1), 0),
            (date(2021, 2, 8), 0),
            (date(2021, 2, 15), 0),
            (date(2021, 2, 22), 1.22),
        ]
        self.assertEqual(result, expect)

    def test_get_total_by_months(self):
        from_date = date(2021, 1, 1)
        to_date = date(2021, 2, 28)
        result = self.service.get_total_by_months(from_date=from_date, to_date=to_date)
        expect = [
            (date(2021, 1, 1), 1),
            (date(2021, 2, 1), 5),
        ]
        self.assertEqual(result, expect)

    def test_get_patients_number_by_age(self):
        result = self.service.get_patients_number_by_age()
        expect = [
            ("10歳未満", 1),
            ("30代", 1),
            ("50代", 1),
            ("90歳以上", 2),
        ]
        self.assertEqual(result, expect)

    def test_get_patients_number(self):
        result = self.service.get_patients_number(date(2021, 2, 22))
        expect = 1
        self.assertEqual(result, expect)


class TestMedicalInstitutionService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
            {
                "name": "市立旭川病院",
                "address": "金星町1",
                "phone_number": "0166-29-0202",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "新富・東・金星町",
                "memo": "",
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
                "備考",
            ],
            [
                "新富・東・金星町",
                "市立旭川病院",
                "金星町1",
                "0166-29-0202",
                "1",
                "0",
                "",
            ],
            [
                "大成",
                "道北勤医協一条通病院",
                "旭川市東光1の1",
                "0166-34-0015 予約専用",
                "1",
                "0",
                (
                    "道北勤医協一条通病院及び道北勤医協一条クリニックは、"
                    + "予約専用番号(34-0015)に変更となります。 開始時期は、"
                    + "各医療機関のホームページ及び院内掲示をご覧ください。"
                ),
            ],
        ]
        self.assertEqual(results, expect)

    def test_get_name_list(self):
        results = self.service.get_name_list()
        expect = ["市立旭川病院", "道北勤医協一条通病院"]
        self.assertEqual(results, expect)

    def test_get_area_list(self):
        results = self.service.get_area_list()
        expect = ["新富・東・金星町", "大成"]
        self.assertEqual(results, expect)

    def test_get_locations(self):
        results = self.service.get_locations(area="新富・東・金星町")
        expect = [
            (
                "市立旭川病院",
                "金星町1",
                "0166-29-0202",
                True,
                False,
                "",
                43.778422777778,
                142.365976388889,
            )
        ]
        self.assertEqual(results, expect)


class TestLocationService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
            {
                "medical_institution_name": "市立旭川病院",
                "longitude": 142.365976388889,
                "latitude": 43.778422777778,
            },
        ]
        self.factory = LocationFactory()
        for row in test_data:
            self.factory.create(**row)
        self.service = LocationService()
        self.service.create(self.factory)

    def test_find_all(self):
        results = self.service.find_all()
        location = results.items[0]
        self.assertEqual(location.medical_institution_name, "市立旭川病院")
        self.assertEqual(location.longitude, 142.365976388889)
        self.assertEqual(location.latitude, 43.778422777778)


class TestPressReleaseLinkService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
            {
                "url": "https://www.example.com",
                "publication_date": date(2021, 8, 23),
            },
        ]
        self.factory = PressReleaseLinkFactory()
        for row in test_data:
            self.factory.create(**row)
        self.service = PressReleaseLinkService()
        self.service.create(self.factory)

    def test_find_all(self):
        results = self.service.find_all()
        press_release_link = results.items[0]
        self.assertEqual(press_release_link.url, "https://www.example.com")
        self.assertEqual(press_release_link.publication_date, date(2021, 8, 23))

    def test_latest_publication_date(self):
        results = self.service.get_latest_publication_date()
        self.assertEqual(results, date(2021, 8, 23))


if __name__ == "__main__":
    unittest.main()
