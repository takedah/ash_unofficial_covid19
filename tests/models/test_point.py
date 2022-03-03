import pytest

from ash_unofficial_covid19.errors import DataModelError
from ash_unofficial_covid19.models.point import Point


def test_init():
    with pytest.raises(DataModelError):
        Point(latitude="hoge", longitude="fuga")
    with pytest.raises(DataModelError):
        Point(latitude=-90, longitude=180)


def test_latitude():
    point = Point(latitude=43.7703945, longitude=142.3631408)
    assert point.latitude == 43.7703945


def test_longitude():
    point = Point(latitude=43.7703945, longitude=142.3631408)
    assert point.longitude == 142.3631408
