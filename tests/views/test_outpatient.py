import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.outpatient import OutpatientFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.outpatient import OutpatientService
from ash_unofficial_covid19.views.outpatient import OutpatientView


@pytest.fixture()
def view():
    # 位置情報データのセットアップ
    test_locations_data = [
        {
            "medical_institution_name": "JA北海道厚生連旭川厚生病院",
            "longitude": 142.384931,
            "latitude": 43.758732,
        },
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
            "medical_institution_name": "おうみや内科クリニック",
            "longitude": 142.4027245,
            "latitude": 43.74092591,
        },
    ]
    location_factory = LocationFactory()
    for row in test_locations_data:
        location_factory.create(**row)

    conn = ConnectionPool()
    location_service = LocationService(conn)
    location_service.create(location_factory)

    # 発熱外来のセットアップ
    test_data = [
        {
            "is_outpatient": True,
            "is_positive_patients": True,
            "public_health_care_center": "旭川",
            "medical_institution_name": "市立旭川病院",
            "city": "旭川市",
            "address": "旭川市金星町1丁目1番65号",
            "phone_number": "0166-24-3181",
            "is_target_not_family": False,
            "is_pediatrics": True,
            "mon": "08:30～17:00",
            "tue": "08:30～17:00",
            "wed": "08:30～17:00",
            "thu": "08:30～17:00",
            "fri": "08:30～17:00",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": True,
            "is_online_for_positive_patients": True,
            "is_home_visitation_for_positive_patients": False,
            "memo": "かかりつけ患者及び保健所からの紹介患者に限ります。 https://www.city.asahikawa.hokkaido.jp/hospital/3100/d075882.html",
        },
        {
            "is_outpatient": True,
            "is_positive_patients": False,
            "public_health_care_center": "旭川",
            "medical_institution_name": "JA北海道厚生連旭川厚生病院",
            "city": "旭川市",
            "address": "旭川市1条通24丁目111番地",
            "phone_number": "0166-33-7171",
            "is_target_not_family": True,
            "is_pediatrics": False,
            "mon": "08:30～11:30",
            "tue": "08:30～11:30",
            "wed": "08:30～11:30",
            "thu": "08:30～11:30",
            "fri": "08:30～11:30",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": False,
            "is_online_for_positive_patients": False,
            "is_home_visitation_for_positive_patients": False,
            "memo": "",
        },
        {
            "is_outpatient": True,
            "is_positive_patients": True,
            "public_health_care_center": "旭川",
            "medical_institution_name": "旭川赤十字病院",
            "city": "旭川市",
            "address": "旭川市曙1条1丁目1番1号",
            "phone_number": "0166-22-8111",
            "is_target_not_family": False,
            "is_pediatrics": False,
            "mon": "",
            "tue": "",
            "wed": "",
            "thu": "",
            "fri": "",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": True,
            "is_online_for_positive_patients": False,
            "is_home_visitation_for_positive_patients": False,
            "memo": "「受診・相談センター」または保健所等の指示によら ず 受診した場合,初診時選定療養費を申し受けます。 当番制のため、不定期となっています。詳細はお問い合わせください。",
        },
        {
            "is_outpatient": False,
            "is_positive_patients": True,
            "public_health_care_center": "旭川",
            "medical_institution_name": "おうみや内科クリニック",
            "city": "旭川市",
            "address": "旭川市東光14条5丁目6番6号",
            "phone_number": "0166-39-3636",
            "is_target_not_family": True,
            "is_pediatrics": False,
            "mon": "",
            "tue": "",
            "wed": "",
            "thu": "",
            "fri": "",
            "sat": "",
            "sun": "",
            "is_face_to_face_for_positive_patients": False,
            "is_online_for_positive_patients": False,
            "is_home_visitation_for_positive_patients": False,
            "memo": "",
        },
    ]
    factory = OutpatientFactory()
    for row in test_data:
        factory.create(**row)

    service = OutpatientService(conn)
    service.create(factory)
    view = OutpatientView(conn)

    yield view

    conn.close_connection()


def test_find_by_medical_institution(view):
    results = view.find(medical_institution_name="市立旭川病院")
    result = results.items[0]
    assert result.medical_institution_name == "市立旭川病院"
    assert result.longitude == 142.365976388889
    assert result.latitude == 43.778422777778


def test_find_no_outpatient(view):
    results = view.find(medical_institution_name="おうみや内科クリニック")
    assert results.items == []


def test_find_all(view):
    results = view.find()
    result = results.items[0]
    assert result.medical_institution_name == "JA北海道厚生連旭川厚生病院"
    assert result.longitude == 142.384931
    assert result.latitude == 43.758732
    result = results.items[1]
    assert result.medical_institution_name == "旭川赤十字病院"
    assert result.longitude == 142.348303888889
    assert result.latitude == 43.769628888889


def test_get_medical_institution_list(view):
    results = view.get_medical_institution_list()
    assert (
        results[0]["url"]
        == "JA%E5%8C%97%E6%B5%B7%E9%81%93%E5%8E%9A%E7%94%9F%E9%80%A3%E6%97%AD%E5%B7%9D%E5%8E%9A%E7%94%9F%E7%97%85%E9%99%A2"
    )
    assert results[2]["name"] == "市立旭川病院"


def test_search_by_gps(view):
    results = view.search_by_gps(latitude=43.77082378, longitude=142.3650193)
    most_nearest = results[0]["location"]
    most_farthest = results[2]["location"]
    assert most_nearest.medical_institution_name == "市立旭川病院"
    assert most_farthest.medical_institution_name == "JA北海道厚生連旭川厚生病院"


def test_find_pediatrics(view):
    results = view.find(is_pediatrics=True)
    assert results.items[0].medical_institution_name == "市立旭川病院"
    assert len(results.items) == 1


def test_find_no_pediatrics(view):
    results = view.find(is_pediatrics=False)
    assert results.items[0].medical_institution_name == "JA北海道厚生連旭川厚生病院"
    assert len(results.items) == 2


def test_find_target_not_family(view):
    results = view.find(is_target_not_family=True)
    assert results.items[0].medical_institution_name == "JA北海道厚生連旭川厚生病院"
    assert len(results.items) == 1


def test_find_no_target_not_family(view):
    results = view.find(is_target_not_family=False)
    assert results.items[0].medical_institution_name == "旭川赤十字病院"
    assert results.items[1].medical_institution_name == "市立旭川病院"
    assert len(results.items) == 2


def test_find_medical_institution_name_and_is_pediatrics(view):
    results = view.find(medical_institution_name="旭川赤十字病院", is_pediatrics=False)
    assert results.items[0].medical_institution_name == "旭川赤十字病院"
    assert len(results.items) == 1


def test_find_is_pediatrics_and_is_target_not_family(view):
    results = view.find(is_pediatrics=True, is_target_not_family=False)
    assert results.items[0].medical_institution_name == "市立旭川病院"
    assert len(results.items) == 1
