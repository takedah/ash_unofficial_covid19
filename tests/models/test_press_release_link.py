from datetime import date

from ash_unofficial_covid19.models.press_release_link import PressReleaseLink, PressReleaseLinkFactory


def test_create():
    test_data = {
        "url": "https://www.example.com",
        "publication_date": date(2021, 8, 23),
    }
    factory = PressReleaseLinkFactory()
    # PressReleaseLinkクラスのオブジェクトが生成できるか確認する。
    press_release_link = factory.create(**test_data)
    assert isinstance(press_release_link, PressReleaseLink)
