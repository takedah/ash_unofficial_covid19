import unittest

from ash_unofficial_covid19.models.medical_institution_location_reservation_status import (
    MedicalInstitutionLocationReservationStatus,
    MedicalInstitutionLocationReservationStatusFactory
)


class TestMedicalInstitutionLocationReservationStatusFactory(unittest.TestCase):
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
            "status": "―",
            "target_person": "―",
            "inoculation_time": "―",
            "reservation_status_memo": "詳細は病院のホームページで確認してください。",
        }
        factory = MedicalInstitutionLocationReservationStatusFactory()
        # MedicalInstitutionLocationReservationStatusクラスのオブジェクトが生成できるか確認する。
        medical_institution_location_reservation_status = factory.create(**test_data)
        self.assertTrue(
            isinstance(
                medical_institution_location_reservation_status,
                MedicalInstitutionLocationReservationStatus,
            )
        )


if __name__ == "__main__":
    unittest.main()
