import unittest

from ash_unofficial_covid19.models.reservation_status import (
    ReservationStatusFactory
)
from ash_unofficial_covid19.services.reservation_status import (
    ReservationStatusService
)


class TestReservationStatusService(unittest.TestCase):
    def setUp(self):
        test_data = [
            {
                "medical_institution_name": "市立旭川病院",
                "address": "旭川市金星町1",
                "phone_number": "29-0202 予約専用",
                "status": "―",
                "target": "―",
                "inoculation_time": "―",
                "memo": "詳細は病院のホームページで確認してください。",
            },
            {
                "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
                "address": "旭川市花咲町7",
                "phone_number": "0166-51-3910 予約専用",
                "status": "受付中",
                "target": "かかりつけの方",
                "inoculation_time": "１０月１日〜火・木曜日午後",
                "memo": "",
            },
        ]
        factory = ReservationStatusFactory()
        for row in test_data:
            factory.create(**row)
        self.service = ReservationStatusService()
        self.service.create(factory)

    def test_delete(self):
        results = self.service.delete("市立旭川病院")
        self.assertEqual(results, 1)

    def test_find_all(self):
        results = self.service.find_all()
        reservation_status = results.items[0]
        self.assertEqual(reservation_status.medical_institution_name, "市立旭川病院")
        self.assertEqual(reservation_status.status, "―")
        self.assertEqual(reservation_status.memo, "詳細は病院のホームページで確認してください。")
        reservation_status = results.items[1]
        self.assertEqual(
            reservation_status.medical_institution_name, "独立行政法人国立病院機構旭川医療センター"
        )
        self.assertEqual(reservation_status.status, "受付中")
        self.assertEqual(reservation_status.memo, "")

    def test_get_name_list(self):
        results = self.service.get_name_list()
        expect = [
            "市立旭川病院",
            "独立行政法人国立病院機構旭川医療センター",
        ]
        self.assertEqual(results, expect)


if __name__ == "__main__":
    unittest.main()
