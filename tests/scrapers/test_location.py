import pytest
import requests

from ash_unofficial_covid19.scrapers.location import ScrapeYOLPLocation


@pytest.fixture()
def json_content():
    return """
{
"ResultInfo": {
    "Count": 1,
    "Total": 1,
    "Start": 1,
    "Status": 200,
    "Description": "",
    "Copyright": "",
    "Latency": 0.017
},
"Feature": [
    {
        "Id": "20130710667",
        "Gid": "",
        "Name": "\u5e02\u7acb\u65ed\u5ddd\u75c5\u9662",
        "Geometry": {
            "Type": "point",
            "Coordinates": "142.365976388889,43.778422777778"
        },
        "Category": []
    }
]
}
    """


def test_lists(json_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = json_content
    responce_mock.headers = {"content-type": "application/json"}
    mocker.patch.object(requests, "get", return_value=responce_mock)
    location_data = ScrapeYOLPLocation("市立旭川病院")
    result = location_data.lists[0]
    assert result["medical_institution_name"] == "市立旭川病院"
    assert result["longitude"] == 142.365976388889
    assert result["latitude"] == 43.778422777778
