from datetime import date

import pytest

from ash_unofficial_covid19.errors import DataModelError
from ash_unofficial_covid19.models.patient import (
    AsahikawaPatient,
    AsahikawaPatientFactory,
    HokkaidoPatient,
    HokkaidoPatientFactory,
)


class TestAsahikawaPatient:
    def test_create(self):
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
        factory = AsahikawaPatientFactory()
        # AsahikawaPatientクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_data)
        assert isinstance(patient, AsahikawaPatient)

    @pytest.mark.parametrize(
        "invalid_data,expected",
        [
            (
                {
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
                },
                "識別番号が正しくありません。",
            ),
            (
                {
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
                },
                "情報公開日が正しくありません。",
            ),
        ],
    )
    def test_create_error(self, invalid_data, expected):
        factory = AsahikawaPatientFactory()
        with pytest.raises(DataModelError, match=expected):
            factory.create(**invalid_data)


class TestHokkaidoPatient:
    def test_create(self):
        test_data = {
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
        factory = HokkaidoPatientFactory()
        # HokkaidoPatientクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_data)
        assert isinstance(patient, HokkaidoPatient)
