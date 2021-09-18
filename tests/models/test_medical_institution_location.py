import unittest

from ash_unofficial_covid19.models.medical_institution_location import (
    MedicalInstitutionLocation,
    MedicalInstitutionLocationFactory
)


class TestMedicalInstitutionLocationFactory(unittest.TestCase):
    def test_create(self):
        test_data = {
            "name": "市立旭川病院",
            "address": "金星町1",
            "phone_number": "0166-29-0202",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "",
            "memo": "",
            "target_age": "16歳以上",
            "longitude": 142.365976388889,
            "latitude": 43.778422777778,
        }
        factory = MedicalInstitutionLocationFactory()
        # MedicalInstitutionLocationクラスのオブジェクトが生成できるか確認する。
        medical_institution_location = factory.create(**test_data)
        self.assertTrue(
            isinstance(medical_institution_location, MedicalInstitutionLocation)
        )


if __name__ == "__main__":
    unittest.main()
