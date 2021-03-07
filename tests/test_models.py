import unittest
from datetime import date

from ash_unofficial_covid19.errors import DataModelError
from ash_unofficial_covid19.models import Patient, PatientFactory

test_data = {
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
    "hokkaido_patient_number": 19050,
    "surrounding_status": "調査中",
    "close_contact": "2人",
}
invalid_number_data = {
    "patient_number": "千百二十",
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
    "hokkaido_patient_number": 19050,
    "surrounding_status": "調査中",
    "close_contact": "2人",
}
invalid_date_data = {
    "patient_number": 1120,
    "city_code": "012041",
    "prefecture": "北海道",
    "city_name": "旭川市",
    "publication_date": "2月26日",
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
    "hokkaido_patient_number": 19050,
    "surrounding_status": "調査中",
    "close_contact": "2人",
}


class TestPatientFactory(unittest.TestCase):
    def test_create(self):
        factory = PatientFactory()
        # Patientクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_data)
        self.assertTrue(isinstance(patient, Patient))

        # 識別番号が数値にできない値の場合エラーを返す
        with self.assertRaises(DataModelError):
            factory.create(**invalid_number_data)

        # 情報公開日が正しくない場合エラーを返す
        with self.assertRaises(DataModelError):
            factory.create(**invalid_date_data)


if __name__ == "__main__":
    unittest.main()
