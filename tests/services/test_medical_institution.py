import pytest

from ash_unofficial_covid19.models.medical_institution import MedicalInstitutionFactory
from ash_unofficial_covid19.services.medical_institution import MedicalInstitutionService


@pytest.fixture()
def service():
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
    yield service


def test_delete(service):
    results = service.delete(("市立旭川病院", "16歳以上"))
    assert results == 1


@pytest.mark.parametrize(
    "name,address,phone_number,book_at_medical_institution,book_at_call_center,area,memo,target_age",
    [
        (
            "市立旭川病院",
            "旭川市金星町1",
            "0166-29-0202",
            True,
            False,
            "東・金星町・各条17〜26丁目",
            "",
            "12歳から15歳まで",
        ),
    ],
)
def test_find_all(
    service,
    name,
    address,
    phone_number,
    book_at_medical_institution,
    book_at_call_center,
    area,
    memo,
    target_age,
):
    results = service.find_all()
    medical_institution = results.items[0]
    assert medical_institution.name == name
    assert medical_institution.address == address
    assert medical_institution.phone_number == phone_number
    assert medical_institution.book_at_medical_institution == book_at_medical_institution
    assert medical_institution.book_at_call_center == book_at_call_center
    assert medical_institution.area == area
    assert medical_institution.memo == memo
    assert medical_institution.target_age == target_age


def test_get_name_lists(service):
    results = service.get_name_lists()
    expect = [
        ("市立旭川病院", "12歳から15歳まで"),
        ("市立旭川病院", "16歳以上"),
        ("独立行政法人国立病院機構旭川医療センター", "12歳から15歳まで"),
        ("道北勤医協一条通病院", "16歳以上"),
    ]
    assert results == expect


def test_get_area_list(service):
    results = service.get_area_list()
    expect = ["大成", "新富・東・金星町"]
    assert results == expect


def test_get_pediatric_area_list(service):
    results = service.get_area_list(is_pediatric=True)
    expect = ["東・金星町・各条17〜26丁目", "花咲町・末広・末広東・永山"]
    assert results == expect
