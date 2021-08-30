import unittest
from datetime import date

from ash_unofficial_covid19.models.sapporo_patients_number import (
    SapporoPatientsNumberFactory
)
from ash_unofficial_covid19.services.sapporo_patients_number import (
    SapporoPatientsNumberService
)


class TestSapporoPatientsNumberService(unittest.TestCase):
    @classmethod
    def setUp(self):
        test_data = [
            {
                "publication_date": date(2021, 8, 29),
                "patients_number": 134,
            },
        ]
        self.factory = SapporoPatientsNumberFactory()
        for row in test_data:
            self.factory.create(**row)
        self.service = SapporoPatientsNumberService()
        self.service.create(self.factory)

    def test_find_all(self):
        results = self.service.find_all()
        sapporo_patients_number = results.items[0]
        self.assertEqual(sapporo_patients_number.publication_date, date(2021, 8, 29))
        self.assertEqual(sapporo_patients_number.patients_number, 134)


if __name__ == "__main__":
    unittest.main()
