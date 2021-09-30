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
    ]
    factory = LocationFactory()
    for row in test_data:
        factory.create(**row)
    service = LocationService()
    service.create(factory)
    yield service


def test_find_all(service):
    locations = service.find_all()
    for location in locations.items:
        assert location.medical_institution_name == "市立旭川病院"
        assert location.longitude == 142.365976388889
        assert location.latitude == 43.778422777778
