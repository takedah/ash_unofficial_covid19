import unittest

from ash_unofficial_covid19.models.location import LocationFactory
from ash_unofficial_covid19.services.location import LocationService


class TestLocationService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
            {
                "medical_institution_name": "市立旭川病院",
                "longitude": 142.365976388889,
                "latitude": 43.778422777778,
            },
        ]
        self.factory = LocationFactory()
        for row in test_data:
            self.factory.create(**row)
        self.service = LocationService()
        self.service.create(self.factory)

    def test_find_all(self):
        results = self.service.find_all()
        location = results.items[0]
        self.assertEqual(location.medical_institution_name, "市立旭川病院")
        self.assertEqual(location.longitude, 142.365976388889)
        self.assertEqual(location.latitude, 43.778422777778)


if __name__ == "__main__":
    unittest.main()
