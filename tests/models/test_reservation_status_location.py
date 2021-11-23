from ash_unofficial_covid19.models.reservation_status_location import (
    ReservationStatusLocation,
    ReservationStatusLocationFactory,
)


def test_create():
    test_data = {
        "medical_institution_name": "市立旭川病院",
        "address": "金星町1",
        "phone_number": "0166-29-0202",
        "status": "―",
        "inoculation_time": "―",
        "target_age": "16歳以上",
        "target_family": False,
        "target_not_family": False,
        "target_suberbs": False,
        "target_other": "",
        "longitude": 142.365976388889,
        "latitude": 43.778422777778,
        "memo": "詳細は病院のホームページで確認してください。",
    }
    factory = ReservationStatusLocationFactory()
    # ReservationStatusLocationクラスのオブジェクトが生成できるか確認する。
    reservation_status_location = factory.create(**test_data)
    assert isinstance(
        reservation_status_location,
        ReservationStatusLocation,
    )
