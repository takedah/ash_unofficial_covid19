import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.models.medical_institution import MedicalInstitutionFactory
from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.location import LocationService
from ash_unofficial_covid19.services.medical_institution import MedicalInstitutionService
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService
from ash_unofficial_covid19.views.medical_institution import MedicalInstitutionView


@pytest.fixture()
def view():
    test_data = [
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
            "name": "道北勤医協一条通病院",
            "address": "旭川市東光1の1",
            "phone_number": "0166-34-0015 予約専用",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "大成",
            "memo": "道北勤医協一条通病院及び道北勤医協一条クリニックは、予約専用番号(34-0015)に変更となります。 開始時期は、各医療機関のホームページ及び院内掲示をご覧ください。",
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
    factory = MedicalInstitutionFactory()
    for row in test_data:
        factory.create(**row)
    service = MedicalInstitutionService()
    service.create(factory)

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

    # 予約受付状況データのセットアップ
    test_reservastion_status_data = [
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
            "target_age": "",
            "target_family": True,
            "target_not_family": False,
            "target_suberbs": False,
            "target_other": "",
            "memo": "",
        },
    ]
    reservastion_status_factory = ReservationStatusFactory()
    for row in test_reservastion_status_data:
        reservastion_status_factory.create(**row)
    reservastion_status_service = ReservationStatusService()
    reservastion_status_service.create(reservastion_status_factory)

    view = MedicalInstitutionView()
    yield view


def test_find(view):
    result = view.find(name="市立旭川病院")
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
    assert result.target_person == ""
    assert result.inoculation_time == "―"
    assert result.reservation_status_memo == "詳細は病院のホームページで確認してください。"


def test_find_area(view):
    results = view.find_area(area="新富・東・金星町")
    result = results[0]
    assert result[0].name == "市立旭川病院"
    assert result[0].address == "旭川市金星町1"
    assert result[0].phone_number == "0166-29-0202"
    assert result[0].book_at_medical_institution is True
    assert result[0].book_at_call_center is False
    assert result[0].area == "新富・東・金星町"
    assert result[0].memo == ""
    assert result[0].target_age == "16歳以上"
    assert result[0].latitude == 43.778422777778
    assert result[0].longitude == 142.365976388889
    assert result[0].status == "―"
    assert result[0].target_person == ""
    assert result[0].inoculation_time == "―"
    assert result[0].reservation_status_memo == "詳細は病院のホームページで確認してください。"
    assert result[1] == "%E5%B8%82%E7%AB%8B%E6%97%AD%E5%B7%9D%E7%97%85%E9%99%A2"


def test_get_area_list(view):
    results = view.get_area_list()
    expect = [
        ("大成", "%E5%A4%A7%E6%88%90"),
        ("新富・東・金星町", "%E6%96%B0%E5%AF%8C%E3%83%BB%E6%9D%B1%E3%83%BB%E9%87%91%E6%98%9F%E7%94%BA"),
    ]
    assert results == expect


def test_get_csv(view):
    results = view.get_csv()
    expect = (
        '"地区","医療機関名","住所","電話","かかりつけの医療機関で予約ができます","コールセンターやインターネットで予約ができます","対象年齢","備考"'
        + "\n"
        + '"東・金星町・各条17〜26丁目","市立旭川病院","旭川市金星町1","0166-29-0202","1","0","12歳から15歳まで",""'
        + "\n"
        + '"花咲町・末広・末広東・永山","独立行政法人国立病院機構旭川医療センター","旭川市花咲町7","0166-51-3910 予約専用","1","0","12歳から15歳まで",""'
        + "\n"
        + '"大成","道北勤医協一条通病院","旭川市東光1の1","0166-34-0015 予約専用","1","0","16歳以上",'
        + '"道北勤医協一条通病院及び道北勤医協一条クリニックは、予約専用番号(34-0015)に変更となります。 開始時期は、各医療機関のホームページ及び院内掲示をご覧ください。"'
        + "\n"
        + '"新富・東・金星町","市立旭川病院","旭川市金星町1","0166-29-0202","1","0","16歳以上",""'
        + "\n"
    )
    assert results == expect
