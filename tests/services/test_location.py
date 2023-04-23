import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.point import PointFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusLocationFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.location import LocationService


@pytest.fixture()
def service():
    test_data = [
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
    factory = LocationFactory()
    for row in test_data:
        factory.create(**row)

    conn = ConnectionPool()
    service = LocationService(conn)
    service.create(factory)

    yield service

    conn.close_connection()


def test_find_all(service):
    results = service.find_all()
    result = results.items[2]
    assert result.medical_institution_name == "市立旭川病院"
    assert result.longitude == 142.365976388889
    assert result.latitude == 43.778422777778


def test_get_distance(service):
    point_factory = PointFactory()
    start_location = point_factory.create(longitude=142.365976388889, latitude=43.778422777778)  # 市立旭川病院
    end_location = point_factory.create(
        longitude=142.3815237271935, latitude=43.798826491523464
    )  # 独立行政法人国立病院機構旭川医療センター
    result = service.get_distance(start_point=start_location, end_point=end_location)
    assert result == 2592.288


def test_get_near_locations(service):
    test_data = [
        {
            "area": "神楽・神楽岡・緑が丘",
            "medical_institution_name": "旭川リハビリテーション病院",
            "division": "春開始接種（12歳以上）",
            "address": "緑が丘東1条1丁目",
            "phone_number": "65-6014 予約専用",
            "vaccine": "ファイザー・モデルナの両方",
            "status": "受付中",
            "inoculation_time": "2/21",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": True,
            "longitude": 142.3871075983558,
            "latitude": 43.73051097382853,
            "memo": "",
        },
        {
            "area": "神楽・神楽岡・緑が丘",
            "medical_institution_name": "旭川医科大学病院",
            "division": "春開始接種（12歳以上）",
            "address": "緑が丘東2条1丁目",
            "phone_number": "65-2111",
            "vaccine": "モデルナのみ",
            "status": "受付停止中",
            "inoculation_time": "",
            "is_target_family": None,
            "is_target_not_family": None,
            "is_target_suberb": True,
            "longitude": 142.38382199835564,
            "latitude": 43.73007572101459,
            "memo": "",
        },
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "division": "春開始接種（12歳以上）",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "vaccine": "モデルナのみ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "longitude": 142.348303888889,
            "latitude": 43.769628888889,
            "memo": "当院ホームページをご確認ください",
        },
        {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "division": "春開始接種（12歳以上）",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "vaccine": "ファイザー・モデルナの両方",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": True,
            "longitude": 142.3815237271935,
            "latitude": 43.798826491523464,
            "memo": "",
        },
        {
            "area": "各条１７～２６丁目・宮前・南地区",
            "medical_institution_name": "森山病院",
            "division": "春開始接種（12歳以上）",
            "address": "宮前2条1丁目",
            "phone_number": "45-2026予約専用",
            "vaccine": "ファイザーのみ",
            "status": "受付中",
            "inoculation_time": "2月28日～8月",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": True,
            "longitude": 142.362565555556,
            "latitude": 43.781208333333,
            "memo": "月・水14:00～15:00",
        },
        {
            "area": "新富・東・金星町地区",
            "medical_institution_name": "市立旭川病院",
            "division": "春開始接種（12歳以上）",
            "address": "金星町1丁目",
            "phone_number": "29-0202予約専用",
            "vaccine": "",
            "status": "",
            "inoculation_time": "",
            "is_target_family": None,
            "is_target_not_family": None,
            "is_target_suberb": True,
            "longitude": 142.365976388889,
            "latitude": 43.778422777778,
            "memo": "",
        },
    ]
    locations = ReservationStatusLocationFactory()
    for d in test_data:
        locations.create(**d)

    current_point_factory = PointFactory()
    current_point = current_point_factory.create(latitude=43.77082378, longitude=142.3650193)

    results = service.get_near_locations(locations=locations, current_point=current_point)
    most_nearest = results[0]["location"]
    most_farthest = results[4]["location"]
    assert most_nearest.medical_institution_name == "市立旭川病院"
    assert most_farthest.medical_institution_name == "旭川医科大学病院"
