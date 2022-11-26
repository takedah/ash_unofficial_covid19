from datetime import date

import pytest

from ash_unofficial_covid19.models.patients_number import PatientsNumberFactory
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.views.patients_number import PatientsNumberView


class TestPatientsNumberView:
    @pytest.fixture()
    def view(self):
        test_data = [
            {
                "publication_date": date(2020, 2, 23),
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
                "publication_date": date(2020, 2, 24),
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
        view = PatientsNumberView(date(2020, 2, 25))

        yield view

    def test_get_daily_total_csv(self, view):
        result = view.get_daily_total_csv()
        expect = '"公表日","陽性患者数"\n"2020-02-23","97"\n"2020-02-24","102"\n"2020-02-25","0"\n'
        assert result == expect

    def test_get_daily_total_json(self, view):
        result = view.get_daily_total_json()
        expect = '{"2020-02-23": 97, "2020-02-24": 102, "2020-02-25": 0}'
        assert result == expect

    def test_get_daily_total_per_age_csv(self, view):
        result = view.get_daily_total_per_age_csv()
        expect = (
            '"公表日","10歳未満","10代","20代","30代","40代","50代","60代","70代","80代","90歳以上","調査中等"\n'
            + '"2020-02-23","12","19","12","14","13","15","3","2","2","0","5"\n'
            + '"2020-02-24","18","19","14","14","16","8","5","2","1","0","5"\n'
            + '"2020-02-25","0","0","0","0","0","0","0","0","0","0","0"\n'
        )
        assert result == expect

    def test_get_daily_total_per_age_json(self, view):
        result = view.get_daily_total_per_age_json()
        expect = (
            '{"2020-02-23": '
            + '{"age_under_10": 12, "age_10s": 19, "age_20s": 12, "age_30s": 14, "age_40s": 13, "age_50s": 15, '
            + '"age_60s": 3, "age_70s": 2, "age_80s": 2, "age_over_90": 0, "investigating": 5}, '
            + '"2020-02-24": '
            + '{"age_under_10": 18, "age_10s": 19, "age_20s": 14, "age_30s": 14, "age_40s": 16, "age_50s": 8, '
            + '"age_60s": 5, "age_70s": 2, "age_80s": 1, "age_over_90": 0, "investigating": 5}, '
            + '"2020-02-25": '
            + '{"age_under_10": 0, "age_10s": 0, "age_20s": 0, "age_30s": 0, "age_40s": 0, "age_50s": 0, '
            + '"age_60s": 0, "age_70s": 0, "age_80s": 0, "age_over_90": 0, "investigating": 0}}'
        )
        assert result == expect
