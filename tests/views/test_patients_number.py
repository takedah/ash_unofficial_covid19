from datetime import date

import pytest

from ash_unofficial_covid19.models.patients_number import PatientsNumberFactory
from ash_unofficial_covid19.services.database import ConnectionPool
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.views.patients_number import (
    ByAgeView,
    DailyTotalView,
    MonthTotalView,
    PatientsNumberView,
    PerHundredThousandPopulationView,
    WeeklyPerAgeView,
)


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

        conn = ConnectionPool()
        service = PatientsNumberService(conn)
        service.create(factory)
        view = PatientsNumberView(date(2020, 2, 25), conn)

        yield view

        conn.close_connection()

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


class TestDailyTotalView:
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

        conn = ConnectionPool()
        service = PatientsNumberService(conn)
        service.create(factory)
        view = DailyTotalView(date(2020, 2, 24), conn)

        yield view

        conn.close_connection()

    def test_daily_total_property(self, view):
        assert view.reference_date == "2020/02/24 (月) "
        assert view.most_recent == "102"
        assert view.seven_days_before_most_recent == "0"
        assert view.increase_from_seven_days_before == "+102"
        assert (
            view.graph_alt
            == "2020年02月18日 0人, 2020年02月19日 0人, 2020年02月20日 0人, "
            + "2020年02月21日 0人, 2020年02月22日 0人, 2020年02月23日 97人, "
            + "2020年02月24日 102人"
        )


class TestMonthTotalView:
    @pytest.fixture()
    def view(self):
        conn = ConnectionPool()
        view = MonthTotalView(date(2020, 2, 24), conn)

        yield view

        conn.close_connection()

    def test_month_total_property(self, view):
        assert view.reference_date == "2020/02/24 (月) "
        assert view.this_month == "199"
        assert view.last_month == "0"
        assert view.increase_from_last_month == "+199"
        assert view.graph_alt == "2020年01月 0人, 2020年02月 199人"


class TestByAgeView:
    @pytest.fixture()
    def view(self):
        conn = ConnectionPool()
        view = ByAgeView(date(2020, 2, 24), conn)

        yield view

        conn.close_connection()

    def test_by_age_property(self, view):
        assert (
            view.graph_alt
            == "10歳未満 30人, 10代 38人, 20代 26人, 30代 28人, " + "40代 29人, 50代 23人, 60代 8人, 70代 4人, " + "80代 3人, 90歳以上 0人"
        )


class TestPerHundredThousandPopulationView:
    @pytest.fixture()
    def view(self):
        conn = ConnectionPool()
        view = PerHundredThousandPopulationView(date(2020, 2, 24), conn)

        yield view

        conn.close_connection()

    def test_per_hundred_thousand_population_property(self, view):
        assert view.this_week == "60.68"
        assert view.last_week == "0.0"
        assert view.increase_from_last_week == "+60.68"
        assert view.graph_alt == "2020年02月09日 0.0人, 2020年02月16日 0.0人, 2020年02月23日 60.68人"


class TestWeeklyPerAgeView:
    @pytest.fixture()
    def view(self):
        conn = ConnectionPool()
        view = WeeklyPerAgeView(date(2020, 2, 24), conn)

        yield view

        conn.close_connection()

    def test_weekly_per_age_property(self, view):
        assert (
            view.graph_alt
            == "02月23日以降 10歳未満: 30人,10代: 38人,20代: 26人,30代: 28人,40代: 29人,"
            + "50代: 23人,60代: 8人,70代: 4人,80代: 3人,"
            + "90歳以上: 0人,調査中等: 10人,"
        )
