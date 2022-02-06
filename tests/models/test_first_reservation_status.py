from ash_unofficial_covid19.models.first_reservation_status import (
    FirstReservationStatus,
    FirstReservationStatusFactory,
    FirstReservationStatusLocation,
    FirstReservationStatusLocationFactory,
)


class TestFirstReservationStatus:
    def test_create(self):
        test_data = {
            "area": "新富・東・金星町地区",
            "medical_institution_name": "市立旭川病院",
            "address": "金星町1丁目",
            "phone_number": "29-0202予約専用",
            "vaccine": None,
            "status": "",
            "inoculation_time": "",
            "target_age": "",
            "is_target_family": None,
            "is_target_not_family": None,
            "is_target_suberb": None,
            "target_other": "",
            "memo": "",
        }
        factory = FirstReservationStatusFactory()
        # FirstReservationStatusクラスのオブジェクトが生成できるか確認する。
        reservation_status = factory.create(**test_data)
        assert isinstance(reservation_status, FirstReservationStatus)


class TestFirstReservationStatusLocation:
    def test_create(self):
        test_data = {
            "area": "新富・東・金星町地区",
            "medical_institution_name": "市立旭川病院",
            "address": "金星町1丁目",
            "phone_number": "29-0202予約専用",
            "vaccine": None,
            "status": "",
            "inoculation_time": "",
            "target_age": "",
            "is_target_family": None,
            "is_target_not_family": None,
            "is_target_suberb": None,
            "target_other": "",
            "longitude": 142.365976388889,
            "latitude": 43.778422777778,
            "memo": "",
        }
        factory = FirstReservationStatusLocationFactory()
        # FirstReservationStatusLocationクラスのオブジェクトが生成できるか確認する。
        reservation_status_location = factory.create(**test_data)
        assert isinstance(
            reservation_status_location,
            FirstReservationStatusLocation,
        )
        # 地区と医療機関名をURLパースした要素が生成されているか確認する。
        assert (
            reservation_status_location.area_url
            == "%E6%96%B0%E5%AF%8C%E3%83%BB%E6%9D%B1%E3%83%BB%E9%87%91%E6%98%9F%E7%94%BA%E5%9C%B0%E5%8C%BA"
        )
        assert (
            reservation_status_location.medical_institution_name_url
            == "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2"
        )
