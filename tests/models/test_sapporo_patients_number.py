from datetime import date

from ash_unofficial_covid19.models.sapporo_patients_number import (
    SapporoPatientsNumber,
    SapporoPatientsNumberFactory,
)


def test_create():
    test_data = {
        "publication_date": date(2021, 8, 28),
        "patients_number": 274,
    }
    factory = SapporoPatientsNumberFactory()
    # SapporoPatientsNumberクラスのオブジェクトが生成できるか確認する。
    sapporo_patients_number = factory.create(**test_data)
    assert isinstance(sapporo_patients_number, SapporoPatientsNumber)
