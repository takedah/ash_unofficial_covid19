import unittest

from ash_unofficial_covid19.models.reservation_status import (
    ReservationStatus,
    ReservationStatusFactory
)


class TestReservationStatusFactory(unittest.TestCase):
    def test_create(self):
        test_data = {
            "medical_institution_name": "市立旭川病院",
            "address": "金星町１丁目",
            "phone_number": "29-0202 予約専用",
            "status": "―",
            "target": "―",
            "inoculation_time": "―",
            "memo": "詳細は病院のホームページで確認してください。",
        }
        factory = ReservationStatusFactory()
        # ReservationStatusクラスのオブジェクトが生成できるか確認する。
        medical_institution = factory.create(**test_data)
        self.assertTrue(isinstance(medical_institution, ReservationStatus))


if __name__ == "__main__":
    unittest.main()
