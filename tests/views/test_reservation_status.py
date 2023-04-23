import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService
from ash_unofficial_covid19.views.reservation_status import ReservationStatusView


@pytest.fixture()
def view():
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
    view = ReservationStatusView(conn)

    yield view

    conn.close_connection()


def test_find_by_medical_institution(view):
    results = view.find(medical_institution_name="独立行政法人国立病院機構旭川医療センター")
    result = results.items[0]
    assert result.medical_institution_name == "独立行政法人国立病院機構旭川医療センター"
    assert result.longitude == 142.3815237271935
    assert result.latitude == 43.798826491523464


def test_find_by_area(view):
    results = view.find(area="花咲町・末広・末広東・東鷹栖地区")
    result = results.items[0]
    assert result.medical_institution_name == "独立行政法人国立病院機構旭川医療センター"
    assert result.longitude == 142.3815237271935
    assert result.latitude == 43.798826491523464


def test_find_all(view):
    results = view.find()
    result = results.items[1]
    assert result.medical_institution_name == "旭川赤十字病院"
    assert result.longitude == 142.348303888889
    assert result.latitude == 43.769628888889


def test_get_area_list(view):
    results = view.get_area_list()
    assert results[0]["name"] == "花咲町・末広・末広東・東鷹栖地区"
    assert results[1]["url"] == "%E8%A5%BF%E5%9C%B0%E5%8C%BA"


def test_get_division_list(view):
    results = view.get_division_list()
    assert results[0]["name"] == "小児接種（３回目以降）"
    assert (
        results[1]["url"]
        == "%E6%98%A5%E9%96%8B%E5%A7%8B%E6%8E%A5%E7%A8%AE%EF%BC%8812%E6%AD%B3%E4%BB%A5%E4%B8%8A%EF%BC%89"
    )


def test_get_medical_institution_list(view):
    results = view.get_medical_institution_list()
    assert results[0]["url"] == "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2"
    assert results[1]["name"] == "独立行政法人国立病院機構旭川医療センター"
