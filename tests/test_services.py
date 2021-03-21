import unittest
from datetime import date

from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.models import (
    AsahikawaPatientFactory,
    HokkaidoPatientFactory
)
from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    HokkaidoPatientService
)

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
        "note": "北海道発表NO.: 3 周囲の患者の発生: No.1092             " + "No.1093 濃厚接触者の状況: 1人",
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
        "residence": "石狩振興局管内",
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


class TestAsahikawaPatientService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.factory = AsahikawaPatientFactory()
        for row in test_data:
            self.factory.create(**row)
        self.db = DB()
        self.service = AsahikawaPatientService(self.db)

    @classmethod
    def tearDownClass(self):
        self.db.close()

    def test_create(self):
        self.service.truncate()
        for item in self.factory.items:
            self.assertTrue(self.service.create(item))
        self.db.commit()

    def test_find(self):
        results = self.service.find()
        patient = results[0]
        self.assertEqual(patient.patient_number, 715)
        self.assertEqual(patient.publication_date, date(2021, 12, 9))
        self.assertEqual(patient.age, "90歳以上")
        self.assertEqual(patient.sex, "女性")

    def test_get_patients_rows(self):
        results = self.service.get_patients_rows()
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

    def test_get_aggregate_by_weeks(self):
        from_date = date(2021, 1, 25)
        to_date = date(2021, 2, 28)
        result = self.service.get_aggregate_by_weeks(
            from_date=from_date, to_date=to_date
        )
        expect = {
            "01-25": 1,
            "02-01": 0,
            "02-08": 0,
            "02-15": 0,
            "02-22": 4,
        }
        self.assertEqual(result, expect)

    def test_get_total_by_months(self):
        from_date = date(2021, 1, 1)
        to_date = date(2021, 2, 28)
        result = self.service.get_total_by_months(from_date=from_date, to_date=to_date)
        expect = {
            "2021-01": 1,
            "2021-02": 5,
        }
        self.assertEqual(result, expect)


class TestHokkaidoPatientService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.factory = HokkaidoPatientFactory()
        for row in test_hokkaido_data:
            self.factory.create(**row)
        self.db = DB()
        self.service = HokkaidoPatientService(self.db)

    @classmethod
    def tearDownClass(self):
        self.db.close()

    def test_create(self):
        self.service.truncate()
        for item in self.factory.items:
            self.assertTrue(self.service.create(item))
        self.db.commit()


if __name__ == "__main__":
    unittest.main()
