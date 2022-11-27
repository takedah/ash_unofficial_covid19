from datetime import date
from io import BytesIO

import pytest

from ash_unofficial_covid19.models.patients_number import PatientsNumberFactory
from ash_unofficial_covid19.services.patients_number import PatientsNumberService
from ash_unofficial_covid19.views.graph import (
    ByAgeGraphView,
    DailyTotalGraphView,
    MonthTotalGraphView,
    PerHundredThousandPopulationGraphView,
    WeeklyPerAgeGraphView,
)


class TestDailyTotalGraphView:
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
        view = DailyTotalGraphView(date(2020, 2, 24))

        yield view

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestMonthTotalGraphView:
    @pytest.fixture()
    def view(self):
        view = MonthTotalGraphView(date(2020, 2, 24))

        yield view

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestByAgeGraphView:
    @pytest.fixture()
    def view(self):
        view = ByAgeGraphView(date(2020, 2, 24))

        yield view

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestPerHundredThousandPopulationGraphView:
    @pytest.fixture()
    def view(self):
        view = PerHundredThousandPopulationGraphView(date(2020, 2, 24))

        yield view

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO


class TestWeeklyPerAgeGraphView:
    @pytest.fixture()
    def view(self):
        view = WeeklyPerAgeGraphView(date(2020, 2, 24))

        yield view

    def test_get_graph_image(self, view):
        graph_image = view.get_graph_image()
        assert type(graph_image) is BytesIO
