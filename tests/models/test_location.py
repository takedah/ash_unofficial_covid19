from ash_unofficial_covid19.models.location import Location, LocationFactory


def test_create():
    test_data = {
        "medical_institution_name": "市立旭川病院",
        "longitude": 142.365976388889,
        "latitude": 43.778422777778,
    }
    factory = LocationFactory()
    # Locationクラスのオブジェクトが生成できるか確認する。
    location = factory.create(**test_data)
    assert isinstance(location, Location)
