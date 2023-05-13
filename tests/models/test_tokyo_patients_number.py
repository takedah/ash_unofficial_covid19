from datetime import date

from ash_unofficial_covid19.models.tokyo_patients_number import TokyoPatientsNumber, TokyoPatientsNumberFactory


def test_create():
    test_data = {
        "publication_date": date(2021, 8, 28),
        "patients_number": 274,
    }
    factory = TokyoPatientsNumberFactory()
    # TokyoPatientsNumberクラスのオブジェクトが生成できるか確認する。
    tokyo_patients_number = factory.create(**test_data)
    assert isinstance(tokyo_patients_number, TokyoPatientsNumber)
