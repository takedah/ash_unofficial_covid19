from datetime import date

import pandas as pd
import pytest
from pandas._testing import assert_frame_equal

from ash_unofficial_covid19.errors import ServiceError
from ash_unofficial_covid19.models.patients_number import PatientsNumberFactory
from ash_unofficial_covid19.services.patients_number import PatientsNumberService


class TestPatientsNumberService:
    @pytest.fixture()
    def service(self):
        test_data = [
            {
                "publication_date": date(2022, 1, 28),
                "age_under_10": 12,
                "age_10s": 19,
                "age_20s": 12,
                "age_30s": 14,
                "age_40s": 13,
                "age_50s": 15,
                "age_60s": 3,
                "age_70s": 2,
                "age_80s": 2,
                "age_over_90": 0,
                "investigating": 5,
            },
            {
                "publication_date": date(2022, 1, 29),
                "age_under_10": 18,
                "age_10s": 19,
                "age_20s": 14,
                "age_30s": 14,
                "age_40s": 16,
                "age_50s": 8,
                "age_60s": 5,
                "age_70s": 2,
                "age_80s": 1,
                "age_over_90": 0,
                "investigating": 5,
            },
        ]
        factory = PatientsNumberFactory()
        for row in test_data:
            factory.create(**row)
        service = PatientsNumberService()
        service.create(factory)

        yield service

    def test_delete(self, service):
        assert service.delete(publication_date=date(2022, 1, 28))
        with pytest.raises(ServiceError):
            service.delete("If arg is not date object.")

    def test_find(self, service):
        # 全件検索
        results = service.find()
        first_result = results.items[0]
        assert first_result.publication_date == date(2022, 1, 28)
        second_result = results.items[1]
        assert second_result.publication_date == date(2022, 1, 29)

        # 報道発表日別検索
        results = service.find(date(2022, 1, 29))
        result = results.items[0]
        assert result.age_under_10 == 18

    def test_get_rows(self, service):
        results = service.get_rows()
        expect = [
            ["2022-01-28", "12", "19", "12", "14", "13", "15", "3", "2", "2", "0", "5"],
            ["2022-01-29", "18", "19", "14", "14", "16", "8", "5", "2", "1", "0", "5"],
        ]
        assert results == expect

    def test_get_aggregate_by_days(self, service):
        from_date = date(2022, 1, 27)
        to_date = date(2022, 1, 29)
        result = service.get_aggregate_by_days(from_date=from_date, to_date=to_date)
        expect = [
            (date(2022, 1, 27), 0),
            (date(2022, 1, 28), 97),
            (date(2022, 1, 29), 102),
        ]
        assert result == expect

    def test_get_aggregate_by_weeks(self, service):
        from_date = date(2022, 1, 20)
        to_date = date(2022, 1, 29)
        result = service.get_aggregate_by_weeks(from_date=from_date, to_date=to_date)
        expect = [
            (date(2022, 1, 20), 0),
            (date(2022, 1, 27), 199),
        ]
        assert result == expect

    def test_get_per_hundred_thousand_population_per_week(self, service):
        from_date = date(2022, 1, 20)
        to_date = date(2022, 1, 29)
        result = service.get_per_hundred_thousand_population_per_week(from_date=from_date, to_date=to_date)
        expect = [
            (date(2022, 1, 20), 0),
            (date(2022, 1, 27), 60.64),
        ]
        assert result == expect

    def test_get_aggregate_by_weeks_per_age(self, service):
        from_date = date(2022, 1, 20)
        to_date = date(2022, 1, 29)
        result = service.get_aggregate_by_weeks_per_age(from_date=from_date, to_date=to_date)
        expect = pd.DataFrame(
            [
                [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [30, 38, 26, 28, 29, 23, 8, 4, 3, 0, 10],
            ],
            columns=[
                "10歳未満",
                "10代",
                "20代",
                "30代",
                "40代",
                "50代",
                "60代",
                "70代",
                "80代",
                "90歳以上",
                "調査中等",
            ],
            index=[
                date(2022, 1, 20),
                date(2022, 1, 27),
            ],
        )
        assert_frame_equal(result, expect)

    def test_get_patients_number_by_age(self, service):
        from_date = date(2022, 1, 20)
        to_date = date(2022, 1, 29)
        result = service.get_patients_number_by_age(from_date=from_date, to_date=to_date)
        expect = [
            ("10歳未満", 30),
            ("10代", 38),
            ("20代", 26),
            ("30代", 28),
            ("40代", 29),
            ("50代", 23),
            ("60代", 8),
            ("70代", 4),
            ("80代", 3),
            ("90歳以上", 0),
        ]
        assert result == expect

    def test_get_total_by_months(self, service):
        from_date = date(2021, 12, 28)
        to_date = date(2022, 1, 29)
        result = service.get_total_by_months(from_date=from_date, to_date=to_date)
        expect = [
            (date(2021, 12, 28), 0),
            (date(2022, 1, 28), 199),
        ]
        assert result == expect
