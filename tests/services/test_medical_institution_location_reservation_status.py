import pytest

from ash_unofficial_covid19.errors import ServiceError
from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.medical_institution import MedicalInstitutionFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.medical_institution import MedicalInstitutionService
from ash_unofficial_covid19.services.medical_institution_location_reservation_status import (
    MedicalInstitutionLocationReservationStatusService,
)
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService


@pytest.fixture()
def service():
    # 医療機関データのセットアップ
    test_medical_institutions_data = [
        {
            "name": "市立旭川病院",
            "address": "旭川市金星町1",
            "phone_number": "0166-29-0202",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "新富・東・金星町",
            "memo": "",
            "target_age": "16歳以上",
        },
        {
            "name": "市立旭川病院",
            "address": "旭川市金星町1",
            "phone_number": "0166-29-0202",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "東・金星町・各条17〜26丁目",
            "memo": "",
            "target_age": "12歳から15歳まで",
        },
        {
            "name": "独立行政法人国立病院機構旭川医療センター",
            "address": "旭川市花咲町7",
            "phone_number": "0166-51-3910 予約専用",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "花咲町・末広・末広東・永山",
            "memo": "",
            "target_age": "12歳から15歳まで",
        },
    ]
    medical_institution_factory = MedicalInstitutionFactory()
    for row in test_medical_institutions_data:
        medical_institution_factory.create(**row)
    medical_institution_service = MedicalInstitutionService()
    medical_institution_service.create(medical_institution_factory)

    # 位置情報データのセットアップ
    test_locations_data = [
        {
            "medical_institution_name": "市立旭川病院",
            "longitude": 142.365976388889,
            "latitude": 43.778422777778,
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
            "target": "―",
            "inoculation_time": "―",
            "memo": "詳細は病院のホームページで確認してください。",
        },
    ]
    reservation_status_factory = ReservationStatusFactory()
    for row in test_reservation_status_data:
        reservation_status_factory.create(**row)
    reservation_status_service = ReservationStatusService()
    reservation_status_service.create(reservation_status_factory)

    service = MedicalInstitutionLocationReservationStatusService()
    yield service


def test_find(service):
    result = service.find(name="市立旭川病院")
    assert result.name == "市立旭川病院"
    assert result.address == "旭川市金星町1"
    assert result.phone_number == "0166-29-0202"
    assert result.book_at_medical_institution is True
    assert result.book_at_call_center is False
    assert result.area == "新富・東・金星町"
    assert result.memo == ""
    assert result.target_age == "16歳以上"
    assert result.latitude == 43.778422777778
    assert result.longitude == 142.365976388889
    assert result.status == "―"
    assert result.target_person == "―"
    assert result.inoculation_time == "―"
    assert result.reservation_status_memo == "詳細は病院のホームページで確認してください。"


def test_find_pediatric(service):
    result = service.find(name="市立旭川病院", is_pediatric=True)
    assert result.name == "市立旭川病院"
    assert result.address == "旭川市金星町1"
    assert result.phone_number == "0166-29-0202"
    assert result.book_at_medical_institution is True
    assert result.book_at_call_center is False
    assert result.area == "東・金星町・各条17〜26丁目"
    assert result.memo == ""
    assert result.target_age == "12歳から15歳まで"
    assert result.latitude == 43.778422777778
    assert result.longitude == 142.365976388889
    assert result.status == "―"
    assert result.target_person == "―"
    assert result.inoculation_time == "―"
    assert result.reservation_status_memo == "詳細は病院のホームページで確認してください。"


def test_not_exist_medical_institution(service):
    with pytest.raises(ServiceError):
        service.find(name="hoge")


def test_find_area(service):
    results = service.find_area(area="新富・東・金星町")
    result = results.items[0]
    assert result.name == "市立旭川病院"
    assert result.address == "旭川市金星町1"
    assert result.phone_number == "0166-29-0202"
    assert result.book_at_medical_institution is True
    assert result.book_at_call_center is False
    assert result.area == "新富・東・金星町"
    assert result.memo == ""
    assert result.target_age == "16歳以上"
    assert result.latitude == 43.778422777778
    assert result.longitude == 142.365976388889
    assert result.status == "―"
    assert result.target_person == "―"
    assert result.inoculation_time == "―"
    assert result.reservation_status_memo == "詳細は病院のホームページで確認してください。"


def test_find_area_pediatric(service):
    results = service.find_area(area="東・金星町・各条17〜26丁目", is_pediatric=True)
    result = results.items[0]
    assert result.name == "市立旭川病院"
    assert result.address == "旭川市金星町1"
    assert result.phone_number == "0166-29-0202"
    assert result.book_at_medical_institution is True
    assert result.book_at_call_center is False
    assert result.area == "東・金星町・各条17〜26丁目"
    assert result.memo == ""
    assert result.target_age == "12歳から15歳まで"
    assert result.latitude == 43.778422777778
    assert result.longitude == 142.365976388889
    assert result.status == "―"
    assert result.target_person == "―"
    assert result.inoculation_time == "―"
    assert result.reservation_status_memo == "詳細は病院のホームページで確認してください。"


def test_not_exist_area(service):
    with pytest.raises(ServiceError):
        service.find_area(area="fuga")
