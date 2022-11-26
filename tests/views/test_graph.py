from datetime import date
from io import BytesIO

import pytest

from ash_unofficial_covid19.models.patients_number import PatientsNumberFactory
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.views.graph import (
    ByAgeView,
    DailyTotalView,
    MonthTotalView,
    PerHundredThousandPopulationView,
    WeeklyPerAgeView,
)


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
        service = PatientsNumberService()
        service.create(factory)
        view = DailyTotalView(date(2020, 2, 24))

        yield view

    def test_daily_total_property(self, view):
        assert view.today == "2020/02/24 (月) "
        assert view.most_recent == "102"
        assert view.seven_days_before_most_recent == "0"
        assert view.increase_from_seven_days_before == "+102"
        assert (
            view.graph_alt
            == "2020年02月18日 0人, 2020年02月19日 0人, 2020年02月20日 0人, "
            + "2020年02月21日 0人, 2020年02月22日 0人, 2020年02月23日 97人, "
            + "2020年02月24日 102人"
        )

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestMonthTotalView:
    @pytest.fixture()
    def view(self):
        view = MonthTotalView(date(2020, 2, 24))

        yield view

    def test_month_total_property(self, view):
        assert view.today == "2020/02/24 (月) "
        assert view.this_month == "199"
        assert view.last_month == "0"
        assert view.increase_from_last_month == "+199"
        assert view.graph_alt == "2020年01月 0人, 2020年02月 199人"

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestByAgeView:
    @pytest.fixture()
    def view(self):
        view = ByAgeView(date(2020, 2, 24))

        yield view

    def test_by_age_property(self, view):
        assert (
            view.graph_alt
            == "10歳未満 30人, 10代 38人, 20代 26人, 30代 28人, " + "40代 29人, 50代 23人, 60代 8人, 70代 4人, " + "80代 3人, 90歳以上 0人"
        )

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestPerHundredThousandPopulationView:
    @pytest.fixture()
    def view(self):
        view = PerHundredThousandPopulationView(date(2020, 2, 24))

        yield view

    def test_per_hundred_thousand_population_property(self, view):
        assert view.this_week == "60.68"
        assert view.last_week == "0.0"
        assert view.increase_from_last_week == "+60.68"
        assert view.graph_alt == "2020年02月09日 0.0人, 2020年02月16日 0.0人, 2020年02月23日 60.68人"

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestWeeklyPerAgeView:
    @pytest.fixture()
    def view(self):
        view = WeeklyPerAgeView(date(2020, 2, 24))

        yield view

    def test_weekly_per_age_property(self, view):
        assert (
            view.graph_alt
            == "02月23日以降 10歳未満: 30人,10代: 38人,20代: 26人,30代: 28人,40代: 29人,"
            + "50代: 23人,60代: 8人,70代: 4人,80代: 3人,"
            + "90歳以上: 0人,調査中等: 10人,"
        )

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO
