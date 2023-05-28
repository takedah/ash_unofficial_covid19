import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.outpatient import OutpatientFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.outpatient import OutpatientService


@pytest.fixture()
def service():
    # 位置情報データのセットアップ
    test_locations_data = [
        {
            "medical_institution_name": "JA北海道厚生連 旭川厚生病院",
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
            "is_target_family": False,
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
            "medical_institution_name": "JA北海道厚生連 旭川厚生病院",
            "city": "旭川市",
            "address": "旭川市1条通24丁目111番地",
            "phone_number": "0166-33-7171",
            "is_target_family": True,
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
            "is_target_family": False,
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
    ]
    factory = OutpatientFactory()
    for row in test_data:
        factory.create(**row)

    service = OutpatientService(conn)
    service.create(factory)

    yield service

    conn.close_connection()


def test_delete(service):
    results = service.delete("旭川赤十字病院")
    assert results


def test_get_medical_institution_list(service):
    results = service.get_medical_institution_list()
    expect = [
        "JA北海道厚生連 旭川厚生病院",
        "市立旭川病院",
        "旭川赤十字病院",
    ]
    assert results == expect


def test_find_by_medical_institution(service):
    results = service.find(medical_institution_name="市立旭川病院")
    result = results.items[0]
    assert result.medical_institution_name == "市立旭川病院"
    assert result.longitude == 142.365976388889
    assert result.latitude == 43.778422777778


def test_find_all(service):
    results = service.find()
    result = results.items[0]
    assert result.medical_institution_name == "JA北海道厚生連 旭川厚生病院"
    assert result.longitude == 142.384931
    assert result.latitude == 43.758732
    result = results.items[1]
    assert result.medical_institution_name == "旭川赤十字病院"
    assert result.longitude == 142.348303888889
    assert result.latitude == 43.769628888889
