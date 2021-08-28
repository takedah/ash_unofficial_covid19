import unittest

from ash_unofficial_covid19.scrapers.location import ScrapeYOLPLocation


class TestScrapeYOLPLocation(unittest.TestCase):
    def test_lists(self):
        location_data = ScrapeYOLPLocation("市立旭川病院")
        self.assertEqual(location_data.lists[0]["medical_institution_name"], "市立旭川病院")
        self.assertEqual(location_data.lists[0]["longitude"], 142.365976388889)
        self.assertEqual(location_data.lists[0]["latitude"], 43.778422777778)


if __name__ == "__main__":
    unittest.main()
