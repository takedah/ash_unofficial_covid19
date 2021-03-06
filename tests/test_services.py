import unittest
from datetime import date

from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.models import PatientFactory
from ash_unofficial_covid19.services import PatientService

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
        "note": "北海道発表NO.: 19080 周囲の患者の発生: "
        + "No.1072 No.1094 No.1107 No.1108 濃厚接触者の状況: 0人",
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
        "note": "北海道発表NO.: 19050 周囲の患者の発生: 調査中 濃厚接触者の状況: 2人",
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
        "note": "北海道発表NO.: 19004 周囲の患者の発生: No.1092             "
        + "No.1093 濃厚接触者の状況: 1人",
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
    },
]


class TestPatientService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.factory = PatientFactory()
        for row in test_data:
            self.factory.create(**row)
        self.db = DB()
        self.service = PatientService(self.db)

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
        self.assertEqual(patient.patient_number, 1121)
        self.assertEqual(patient.publication_date, date(2021, 2, 27))
        self.assertEqual(patient.age, "30代")
        self.assertEqual(patient.sex, "男性")

    def test_get_patients_rows(self):
        results = self.service.get_patients_rows()
        expect = [
            [
                "1121",
                "012041",
                "北海道",
                "旭川市",
                "2021-02-27",
                "",
                "旭川市",
                "30代",
                "男性",
                "",
                "",
                "",
                "",
                "",
                "北海道発表NO.: 19080 周囲の患者の発生: "
                + "No.1072 No.1094 No.1107 No.1108 濃厚接触者の状況: 0人",
            ],
            [
                "1120",
                "012041",
                "北海道",
                "旭川市",
                "2021-02-26",
                "",
                "旭川市",
                "50代",
                "女性",
                "",
                "",
                "",
                "",
                "",
                "北海道発表NO.: 19050 周囲の患者の発生: 調査中 濃厚接触者の状況: 2人",
            ],
            [
                "1119",
                "012041",
                "北海道",
                "旭川市",
                "2021-02-25",
                "",
                "旭川市",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "北海道発表NO.: 19004 周囲の患者の発生: No.1092             "
                + "No.1093 濃厚接触者の状況: 1人",
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
        ]
        self.assertEqual(results, expect)


if __name__ == "__main__":
    unittest.main()
