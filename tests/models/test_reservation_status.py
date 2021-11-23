from ash_unofficial_covid19.models.reservation_status import ReservationStatus, ReservationStatusFactory


def test_create():
    test_data = {
        "medical_institution_name": "市立旭川病院",
        "address": "金星町１丁目",
        "phone_number": "29-0202 予約専用",
        "inoculation_time": "―",
        "status": "―",
        "target_age": "",
        "target_family": False,
        "target_not_family": False,
        "target_suberbs": False,
        "target_other": "",
        "memo": "詳細は病院のホームページで確認してください。",
    }
    factory = ReservationStatusFactory()
    # ReservationStatusクラスのオブジェクトが生成できるか確認する。
    reservation_status = factory.create(**test_data)
    assert isinstance(reservation_status, ReservationStatus)
