import unittest

from ash_unofficial_covid19.models.location import Location, LocationFactory


class TestLocationFactory(unittest.TestCase):
    def test_create(self):
        test_location_data = {
            "medical_institution_name": "市立旭川病院",
            "longitude": 142.365976388889,
            "latitude": 43.778422777778,
        }
        factory = LocationFactory()
        # Locationクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_location_data)
        self.assertTrue(isinstance(patient, Location))


if __name__ == "__main__":
    unittest.main()
