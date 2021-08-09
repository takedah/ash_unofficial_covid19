import unittest
from datetime import date

from ash_unofficial_covid19.errors import DataModelError
from ash_unofficial_covid19.models import (
    AsahikawaPatient,
    AsahikawaPatientFactory,
    HokkaidoPatient,
    HokkaidoPatientFactory,
    MedicalInstitution,
    MedicalInstitutionFactory
)

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
test_hokkaido_data = {
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
}
test_medical_institution_data = {
    "name": "市立旭川病院",
    "address": "金星町1",
    "phone_number": "0166-29-0202",
    "book_at_medical_institution": True,
    "book_at_call_center": False,
    "area": "",
    "memo": "",
}


class TestAsahikawaPatientFactory(unittest.TestCase):
    def test_create(self):
        factory = AsahikawaPatientFactory()
        # AsahikawaPatientクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_data)
        self.assertTrue(isinstance(patient, AsahikawaPatient))

        # 識別番号が数値にできない値の場合エラーを返す
        with self.assertRaises(DataModelError):
            factory.create(**invalid_number_data)

        # 情報公開日が正しくない場合エラーを返す
        with self.assertRaises(DataModelError):
            factory.create(**invalid_date_data)


class TestHokkaidoPatientFactory(unittest.TestCase):
    def test_create(self):
        factory = HokkaidoPatientFactory()
        # HokkaidoPatientクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_hokkaido_data)
        self.assertTrue(isinstance(patient, HokkaidoPatient))


class TestMedicalInstitutionFactory(unittest.TestCase):
    def test_create(self):
        factory = MedicalInstitutionFactory()
        # MedicalInstitutionクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_medical_institution_data)
        self.assertTrue(isinstance(patient, MedicalInstitution))


if __name__ == "__main__":
    unittest.main()
