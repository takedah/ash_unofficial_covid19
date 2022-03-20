import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService


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
    ]
    location_factory = LocationFactory()
    for row in test_locations_data:
        location_factory.create(**row)
    location_service = LocationService()
    location_service.create(location_factory)

    # 予約受付状況のセットアップ
    test_data = [
        {
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
        },
        {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "vaccine": "ファイザー モデルナ",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "target_age": "18歳以上",
            "is_target_family": True,
            "is_target_not_family": False,
            "target_other": "",
            "memo": "",
        },
    ]
    factory = ReservationStatusFactory()
    for row in test_data:
        factory.create(**row)
    service = ReservationStatusService()
    service.create(factory)
    yield service


def test_delete(service):
    results = service.delete(("旭川赤十字病院", "モデルナ"))
    assert results


def test_get_medical_institution_list(service):
    results = service.get_medical_institution_list()
    expect = [
        ("旭川赤十字病院", "モデルナ"),
        ("独立行政法人国立病院機構旭川医療センター", "ファイザー モデルナ"),
    ]
    assert results == expect


def test_get_dicts(service):
    results = service.get_dicts()
    expect = {
        "row0": {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "vaccine": "ファイザー モデルナ",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "target_age": "18歳以上",
            "is_target_family": True,
            "is_target_not_family": False,
            "target_other": "",
            "memo": "",
        },
        "row1": {
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
        },
    }
    assert results == expect


def test_find_by_medical_institution(service):
    results = service.find(medical_institution_name="独立行政法人国立病院機構旭川医療センター")
    result = results.items[0]
    assert result.medical_institution_name == "独立行政法人国立病院機構旭川医療センター"
    assert result.longitude == 142.3815237271935
    assert result.latitude == 43.798826491523464


def test_find_by_area(service):
    results = service.find(area="花咲町・末広・末広東・東鷹栖地区")
    result = results.items[0]
    assert result.medical_institution_name == "独立行政法人国立病院機構旭川医療センター"
    assert result.longitude == 142.3815237271935
    assert result.latitude == 43.798826491523464


def test_find_all(service):
    results = service.find()
    result = results.items[1]
    assert result.medical_institution_name == "旭川赤十字病院"
    assert result.longitude == 142.348303888889
    assert result.latitude == 43.769628888889


def test_get_area_list(service):
    results = service.get_area_list()
    assert results[0] == "花咲町・末広・末広東・東鷹栖地区"
    assert results[1] == "西地区"
