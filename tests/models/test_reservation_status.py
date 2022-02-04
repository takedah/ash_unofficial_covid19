from ash_unofficial_covid19.models.reservation_status import (
    ReservationStatus,
    ReservationStatusFactory,
    ReservationStatusLocation,
    ReservationStatusLocationFactory,
)


class TestReservationStatus:
    def test_create(self):
        test_data = {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "target_age": "",
            "is_target_family": False,
            "is_target_not_family": False,
            "target_other": "当院の患者IDをお持ちの方",
            "memo": "当院ホームページをご確認ください",
        }
        factory = ReservationStatusFactory()
        # ReservationStatusクラスのオブジェクトが生成できるか確認する。
        reservation_status = factory.create(**test_data)
        assert isinstance(reservation_status, ReservationStatus)


class TestReservationStatusLocation:
    def test_create(self):
        test_data = {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "target_age": "",
            "is_target_family": False,
            "is_target_not_family": False,
            "target_other": "当院の患者IDをお持ちの方",
            "longitude": 142.348303888889,
            "latitude": 43.769628888889,
            "memo": "当院ホームページをご確認ください",
        }
        factory = ReservationStatusLocationFactory()
        # ReservationStatusLocationクラスのオブジェクトが生成できるか確認する。
        reservation_status_location = factory.create(**test_data)
        assert isinstance(
            reservation_status_location,
            ReservationStatusLocation,
        )
