import pytest

from ash_unofficial_covid19.errors import ServiceError
from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService
from ash_unofficial_covid19.services.reservation_status_location import ReservationStatusLocationService


@pytest.fixture()
def service():
    # 位置情報データのセットアップ
    test_locations_data = [
        {
            "medical_institution_name": "市立旭川病院",
            "longitude": 142.365976388889,
            "latitude": 43.778422777778,
        },
        {
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "longitude": 142.3815237271935,
            "latitude": 43.798826491523464,
        },
    ]
    location_factory = LocationFactory()
    for row in test_locations_data:
        location_factory.create(**row)
    location_service = LocationService()
    location_service.create(location_factory)

    # 予約受付状況のセットアップ
    test_reservation_status_data = [
        {
            "medical_institution_name": "市立旭川病院",
            "address": "旭川市金星町1",
            "phone_number": "29-0202 予約専用",
            "status": "―",
            "inoculation_time": "―",
            "target_age": "",
            "target_family": False,
            "target_not_family": False,
            "target_suberbs": False,
            "target_other": "",
            "memo": "詳細は病院のホームページで確認してください。",
        },
        {
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "旭川市花咲町7",
            "phone_number": "0166-51-3910 予約専用",
            "status": "受付中",
            "inoculation_time": "１０月１日〜火・木曜日午後",
            "target_age": "指定なし",
            "target_family": True,
            "target_not_family": False,
            "target_suberbs": False,
            "target_other": "",
            "memo": "",
        },
    ]
    reservation_status_factory = ReservationStatusFactory()
    for row in test_reservation_status_data:
        reservation_status_factory.create(**row)
    reservation_status_service = ReservationStatusService()
    reservation_status_service.create(reservation_status_factory)

    service = ReservationStatusLocationService()
    yield service


def test_find(service):
    result = service.find(medical_institution_name="市立旭川病院")
    assert result.medical_institution_name == "市立旭川病院"
    assert result.address == "旭川市金星町1"
    assert result.phone_number == "29-0202 予約専用"
    assert result.status == "―"
    assert result.inoculation_time == "―"
    assert result.target_age == ""
    assert result.target_family == False
    assert result.target_not_family == False
    assert result.target_suberbs == False
    assert result.target_other == ""
    assert result.latitude == 43.778422777778
    assert result.longitude == 142.365976388889
    assert result.memo == "詳細は病院のホームページで確認してください。"


def test_not_exist_medical_institution(service):
    with pytest.raises(ServiceError):
        service.find(medical_institution_name="hoge")


def test_find_all(service):
    results = service.find_all()
    result = results.items[0]
    assert result.medical_institution_name == "独立行政法人国立病院機構旭川医療センター"
    assert result.address == "旭川市花咲町7"
    assert result.phone_number == "0166-51-3910 予約専用"
    assert result.status == "受付中"
    assert result.inoculation_time == "１０月１日〜火・木曜日午後"
    assert result.target_age == "指定なし"
    assert result.target_family == True
    assert result.target_not_family == False
    assert result.target_suberbs == False
    assert result.target_other == ""
    assert result.latitude == 43.798826491523464
    assert result.longitude == 142.3815237271935
    assert result.memo == ""
