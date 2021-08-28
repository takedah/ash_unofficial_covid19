import unittest
from datetime import date

from ash_unofficial_covid19.models.press_release_link import (
    PressReleaseLinkFactory
)
from ash_unofficial_covid19.services.press_release_link import (
    PressReleaseLinkService
)


class TestPressReleaseLinkService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
            {
                "url": "https://www.example.com",
                "publication_date": date(2021, 8, 23),
            },
        ]
        self.factory = PressReleaseLinkFactory()
        for row in test_data:
            self.factory.create(**row)
        self.service = PressReleaseLinkService()
        self.service.create(self.factory)

    def test_find_all(self):
        results = self.service.find_all()
        press_release_link = results.items[0]
        self.assertEqual(press_release_link.url, "https://www.example.com")
        self.assertEqual(press_release_link.publication_date, date(2021, 8, 23))

    def test_latest_publication_date(self):
        results = self.service.get_latest_publication_date()
        self.assertEqual(results, date(2021, 8, 23))


if __name__ == "__main__":
    unittest.main()
