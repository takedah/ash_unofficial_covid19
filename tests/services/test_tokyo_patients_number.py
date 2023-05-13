from datetime import date

import pytest

from ash_unofficial_covid19.models.tokyo_patients_number import TokyoPatientsNumberFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.tokyo_patients_number import TokyoPatientsNumberService


@pytest.fixture()
def service():
    test_data = [
        {
            "publication_date": date(2021, 8, 22),
            "patients_number": 4448,
        },
        {
            "publication_date": date(2021, 8, 23),
            "patients_number": 2537,
        },
        {
            "publication_date": date(2021, 8, 24),
            "patients_number": 4328,
        },
        {
            "publication_date": date(2021, 8, 25),
            "patients_number": 4334,
        },
        {
            "publication_date": date(2021, 8, 26),
            "patients_number": 4783,
        },
        {
            "publication_date": date(2021, 8, 27),
            "patients_number": 4350,
        },
        {
            "publication_date": date(2021, 8, 28),
            "patients_number": 3691,
        },
        {
            "publication_date": date(2021, 8, 29),
            "patients_number": 3124,
        },
    ]
    factory = TokyoPatientsNumberFactory()
    for row in test_data:
        factory.create(**row)

    conn = ConnectionPool()
    service = TokyoPatientsNumberService(conn)
    service.create(factory)

    yield service

    conn.close_connection()


def test_find_all(service):
    results = service.find_all()
    tokyo_patients_number = results.items[0]
    assert tokyo_patients_number.publication_date == date(2021, 8, 29)
    assert tokyo_patients_number.patients_number == 3124


def test_get_aggregate_by_weeks(service):
    from_date = date(2021, 8, 22)
    to_date = date(2021, 8, 29)
    result = service.get_aggregate_by_weeks(from_date=from_date, to_date=to_date)
    expect = [
        (date(2021, 8, 22), 28471),
        (date(2021, 8, 29), 3124),
    ]
    assert result == expect


def test_get_per_hundred_thousand_population_per_week(service):
    from_date = date(2021, 8, 22)
    to_date = date(2021, 8, 29)
    result = service.get_per_hundred_thousand_population_per_week(from_date=from_date, to_date=to_date)
    expect = [
        (date(2021, 8, 22), 202.86),
        (date(2021, 8, 29), 22.26),
    ]
    assert result == expect


def test_get_last_update_date(service):
    result = service.get_last_update_date()
    expect = date(2021, 8, 29)
    assert result == expect
