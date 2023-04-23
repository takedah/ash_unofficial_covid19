import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.database import ConnectionPool
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

    conn = ConnectionPool()
    location_service = LocationService(conn)
    location_service.create(location_factory)

    # 予約受付状況のセットアップ
    test_data = [
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "division": "春開始接種（12歳以上）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "memo": "当院ホームページをご確認ください",
        },
        {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "division": "小児接種（３回目以降）",
            "vaccine": "ファイザー モデルナ",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": None,
            "memo": "",
        },
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "division": "小児接種（３回目以降）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "memo": "かかりつけ患者以外は※条件あり 当院ホームページをご確認ください",
        },
    ]
    factory = ReservationStatusFactory()
    for row in test_data:
        factory.create(**row)

    service = ReservationStatusService(conn)
    service.create(factory)

    yield service

    conn.close_connection()


def test_delete(service):
    results = service.delete(("旭川赤十字病院", "春開始接種（12歳以上）", "モデルナ"))
    assert results


def test_get_medical_institution_list(service):
    results = service.get_medical_institution_list()
    expect = [
        ("旭川赤十字病院", "小児接種（３回目以降）", "モデルナ"),
        ("旭川赤十字病院", "春開始接種（12歳以上）", "モデルナ"),
        ("独立行政法人国立病院機構旭川医療センター", "小児接種（３回目以降）", "ファイザー モデルナ"),
    ]
    assert results == expect


def test_get_dicts(service):
    results = service.get_dicts()
    expect = {
        "row0": {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "division": "小児接種（３回目以降）",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "vaccine": "ファイザー モデルナ",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": None,
            "memo": "",
        },
        "row1": {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "division": "小児接種（３回目以降）",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "memo": "かかりつけ患者以外は※条件あり 当院ホームページをご確認ください",
        },
        "row2": {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "division": "春開始接種（12歳以上）",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
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


def test_find_by_division(service):
    results = service.find(division="春開始接種（12歳以上）")
    result = results.items[0]
    assert result.medical_institution_name == "旭川赤十字病院"
    assert result.longitude == 142.348303888889
    assert result.latitude == 43.769628888889


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


def test_get_division_list(service):
    results = service.get_division_list()
    assert results[0] == "小児接種（３回目以降）"
    assert results[1] == "春開始接種（12歳以上）"
