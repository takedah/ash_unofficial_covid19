import pytest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.services.location import LocationService


@pytest.fixture()
def service():
    test_data = [
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
    ]
    factory = LocationFactory()
    for row in test_data:
        factory.create(**row)
    service = LocationService()
    service.create(factory)
    yield service


def test_find_all(service):
    results = service.find_all()
    result = results.items[0]
    assert result.medical_institution_name == "市立旭川病院"
    assert result.longitude == 142.365976388889
    assert result.latitude == 43.778422777778
