from ash_unofficial_covid19.models.medical_institution_location_reservation_status import (
    MedicalInstitutionLocationReservationStatus,
    MedicalInstitutionLocationReservationStatusFactory,
)


def test_create():
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
        "inoculation_time": "―",
        "reservation_status_target_age": "―",
        "target_family": False,
        "target_not_family": False,
        "target_suberbs": False,
        "target_other": "",
        "reservation_status_memo": "詳細は病院のホームページで確認してください。",
    }
    factory = MedicalInstitutionLocationReservationStatusFactory()
    # MedicalInstitutionLocationReservationStatusクラスのオブジェクトが生成できるか確認する。
    medical_institution_location_reservation_status = factory.create(**test_data)
    assert isinstance(
        medical_institution_location_reservation_status,
        MedicalInstitutionLocationReservationStatus,
    )
