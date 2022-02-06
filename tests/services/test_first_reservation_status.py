import pytest

from ash_unofficial_covid19.models.first_reservation_status import FirstReservationStatusFactory
from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.services.first_reservation_status import FirstReservationStatusService
from ash_unofficial_covid19.services.location import LocationService


@pytest.fixture()
def service():
    # 位置情報データのセットアップ
    test_locations_data = [
        {
            "medical_institution_name": "旭川赤十字病院",
            "longitude": 142.348303888889,
            "latitude": 43.769628888889,
        },
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
        {
            "medical_institution_name": "森山病院",
            "longitude": 142.362565555556,
            "latitude": 43.781208333333,
        },
    ]
    location_factory = LocationFactory()
    for row in test_locations_data:
        location_factory.create(**row)
    location_service = LocationService()
    location_service.create(location_factory)

    # 予約受付状況のセットアップ
    test_data = [
        {
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
        },
        {
            "area": "各条１７～２６丁目・宮前・南地区",
            "medical_institution_name": "森山病院",
            "address": "宮前2条1丁目",
            "phone_number": "45-2026予約専用",
            "vaccine": None,
            "status": "受付中",
            "inoculation_time": "2月28日～8月",
            "target_age": "18歳以上",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": True,
            "target_other": "",
            "memo": "月・水 14:00～15:00",
        },
    ]
    factory = FirstReservationStatusFactory()
    for row in test_data:
        factory.create(**row)
    service = FirstReservationStatusService()
    service.create(factory)
    yield service


def test_delete(service):
    results = service.delete("市立旭川病院")
    assert results


def test_get_medical_institution_list(service):
    results = service.get_medical_institution_list()
    expect = ["市立旭川病院", "森山病院"]
    assert results == expect


def test_find_by_medical_institution(service):
    results = service.find(medical_institution_name="森山病院")
    result = results.items[0]
    assert result.medical_institution_name == "森山病院"
    assert result.longitude == 142.362565555556
    assert result.latitude == 43.781208333333


def test_find_by_area(service):
    results = service.find(area="新富・東・金星町地区")
    result = results.items[0]
    assert result.medical_institution_name == "市立旭川病院"
    assert result.longitude == 142.365976388889
    assert result.latitude == 43.778422777778


def test_find_all(service):
    results = service.find()
    result = results.items[1]
    assert result.medical_institution_name == "市立旭川病院"
    assert result.longitude == 142.365976388889
    assert result.latitude == 43.778422777778


def test_get_areas(service):
    results = service.get_areas()
    assert results.items[0].name == "各条１７～２６丁目・宮前・南地区"
    assert results.items[1].name == "新富・東・金星町地区"
