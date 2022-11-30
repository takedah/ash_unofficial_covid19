from ash_unofficial_covid19.models.baby_reservation_status import (
    BabyReservationStatus,
    BabyReservationStatusFactory,
    BabyReservationStatusLocation,
    BabyReservationStatusLocationFactory,
)


class TestBabyReservationStatus:
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
            "is_target_suberb": None,
            "target_other": "当院の患者IDをお持ちの方",
            "memo": "当院ホームページをご確認ください",
        }
        factory = BabyReservationStatusFactory()
        # BabyReservationStatusクラスのオブジェクトが生成できるか確認する。
        reservation_status = factory.create(**test_data)
        assert isinstance(reservation_status, BabyReservationStatus)


class TestBabyReservationStatusLocation:
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
            "is_target_suberb": None,
            "target_other": "当院の患者IDをお持ちの方",
            "longitude": 142.348303888889,
            "latitude": 43.769628888889,
            "memo": "当院ホームページをご確認ください",
        }
        factory = BabyReservationStatusLocationFactory()
        # BabyReservationStatusLocationクラスのオブジェクトが生成できるか確認する。
        reservation_status_location = factory.create(**test_data)
        assert isinstance(
            reservation_status_location,
            BabyReservationStatusLocation,
        )
        # 地区と医療機関名をURLパースした要素が生成されているか確認する。
        assert reservation_status_location.area_url == "%E8%A5%BF%E5%9C%B0%E5%8C%BA"
        assert (
            reservation_status_location.medical_institution_name_url
            == "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2"
        )
