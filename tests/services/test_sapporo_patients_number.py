from datetime import date

import pytest

from ash_unofficial_covid19.models.sapporo_patients_number import SapporoPatientsNumberFactory
from ash_unofficial_covid19.services.sapporo_patients_number import SapporoPatientsNumberService


@pytest.fixture()
def service():
    test_data = [
        {
            "publication_date": date(2021, 8, 22),
            "patients_number": 253,
        },
        {
            "publication_date": date(2021, 8, 23),
            "patients_number": 220,
        },
        {
            "publication_date": date(2021, 8, 24),
            "patients_number": 289,
        },
        {
            "publication_date": date(2021, 8, 25),
            "patients_number": 285,
        },
        {
            "publication_date": date(2021, 8, 26),
            "patients_number": 186,
        },
        {
            "publication_date": date(2021, 8, 27),
            "patients_number": 274,
        },
        {
            "publication_date": date(2021, 8, 28),
            "patients_number": 198,
        },
        {
            "publication_date": date(2021, 8, 29),
            "patients_number": 134,
        },
    ]
    factory = SapporoPatientsNumberFactory()
    for row in test_data:
        factory.create(**row)
    service = SapporoPatientsNumberService()
    service.create(factory)
    yield service


def test_find_all(service):
    results = service.find_all()
    sapporo_patients_number = results.items[0]
    assert sapporo_patients_number.publication_date == date(2021, 8, 29)
    assert sapporo_patients_number.patients_number == 134


def test_get_aggregate_by_weeks(service):
    from_date = date(2021, 8, 22)
    to_date = date(2021, 8, 29)
    result = service.get_aggregate_by_weeks(from_date=from_date, to_date=to_date)
    expect = [
        (date(2021, 8, 22), 1705),
        (date(2021, 8, 29), 134),
    ]
    assert result == expect


def test_get_per_hundred_thousand_population_per_week(service):
    from_date = date(2021, 8, 22)
    to_date = date(2021, 8, 29)
    result = service.get_per_hundred_thousand_population_per_week(from_date=from_date, to_date=to_date)
    expect = [
        (date(2021, 8, 22), 86.95),
        (date(2021, 8, 29), 6.83),
    ]
    assert result == expect
