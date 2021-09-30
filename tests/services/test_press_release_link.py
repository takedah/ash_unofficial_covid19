from datetime import date

import pytest

from ash_unofficial_covid19.models.press_release_link import PressReleaseLinkFactory
from ash_unofficial_covid19.services.press_release_link import PressReleaseLinkService


@pytest.fixture()
def service():
    test_data = [
        {
            "url": "https://www.example.com",
            "publication_date": date(2021, 8, 23),
        },
    ]
    factory = PressReleaseLinkFactory()
    for row in test_data:
        factory.create(**row)
    service = PressReleaseLinkService()
    service.create(factory)
    yield service


def test_find_all(service):
    results = service.find_all()
    press_release_link = results.items[0]
    assert press_release_link.url == "https://www.example.com"
    assert press_release_link.publication_date == date(2021, 8, 23)


def test_latest_publication_date(service):
    results = service.get_latest_publication_date()
    assert results == date(2021, 8, 23)
