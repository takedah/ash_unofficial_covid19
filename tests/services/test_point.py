from ash_unofficial_covid19.models.point import PointFactory
from ash_unofficial_covid19.services.point import PointService


def test_get_distance():
    factory = PointFactory()
    start_point = factory.create(
        **{
            "longitude": 142.365976388889,
            "latitude": 43.778422777778,
        }
    )
    end_point = factory.create(
        **{
            "longitude": 142.3815237271935,
            "latitude": 43.798826491523464,
        }
    )
    result = PointService.get_distance(start_point=start_point, end_point=end_point)
    assert result == 2592.288
