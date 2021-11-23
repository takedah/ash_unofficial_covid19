import pytest

from ash_unofficial_covid19.models.reservation_status import ReservationStatusFactory
from ash_unofficial_covid19.services.reservation_status import ReservationStatusService


@pytest.fixture()
def service():
    test_data = [
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
            "target_age": "指定なし",
            "target_family": True,
            "target_not_family": False,
            "target_suberbs": False,
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
    results = service.delete("市立旭川病院")
    assert results


def test_find_all(service):
    results = service.find_all()
    reservation_status = results.items[0]
    assert reservation_status.medical_institution_name == "市立旭川病院"
    assert reservation_status.status == "―"
    assert reservation_status.memo == "詳細は病院のホームページで確認してください。"


def test_get_name_list(service):
    results = service.get_name_list()
    expect = [
        "市立旭川病院",
        "独立行政法人国立病院機構旭川医療センター",
    ]
    assert results == expect
