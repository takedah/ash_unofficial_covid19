import unittest
from datetime import date

from ash_unofficial_covid19.models.press_release_link import (
    PressReleaseLink,
    PressReleaseLinkFactory
)


class TestPressReleaseLinkFactory(unittest.TestCase):
    def test_create(self):
        test_press_release_data = {
            "url": "https://www.example.com",
            "publication_date": date(2021, 8, 23),
        }
        factory = PressReleaseLinkFactory()
        # PressReleaseLinkクラスのオブジェクトが生成できるか確認する。
        patient = factory.create(**test_press_release_data)
        self.assertTrue(isinstance(patient, PressReleaseLink))


if __name__ == "__main__":
    unittest.main()
