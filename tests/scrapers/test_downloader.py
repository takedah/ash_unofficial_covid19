import json

import pytest
import requests
from requests import HTTPError, Timeout

from ash_unofficial_covid19.errors import HTTPDownloadError
from ash_unofficial_covid19.scrapers.downloader import (
    DownloadedCSV,
    DownloadedHTML,
    DownloadedJSON,
    DownloadedPDF,
)


class TestDownloadedHTML:
    @pytest.fixture()
    def html_content(self):
        return """
<table cellspacing="1" cellpadding="1" style="width: 660px;">
    <caption>新型コロナウイルス感染症の市内発生状況</caption>
    <tbody>
        <tr>
            <th nowrap="nowrap">NO.</th>
            <th nowrap="nowrap">
            <p>北海道発表</p>
            <p>NO.</p>
            </th>
            <th nowrap="nowrap">判明日</th>
            <th nowrap="nowrap">年代</th>
            <th nowrap="nowrap">性別 </th>
            <th nowrap="nowrap">居住地</th>
            <th>周囲の患者の発生</th>
            <th>
            <p>濃厚接触者の状況</p>
            </th>
        </tr>
        <tr>
            <td nowrap="nowrap">1121</td>
            <td>19080</td>
            <td nowrap="nowrap">2月27日</td>
            <td nowrap="nowrap">30代</td>
            <td nowrap="nowrap">男性</td>
            <td>旭川市</td>
            <td>
            <p>No.1072</p>
            <p>No.1094</p>
            <p>No.1107</p>
            <p>No.1108</p>
            </td>
            <td>0人</td>
        </tr>
        <tr>
            <td nowrap="nowrap">1120</td>
            <td>19050</td>
            <td nowrap="nowrap">2 月26日</td>
            <td nowrap="nowrap">50代</td>
            <td nowrap="nowrap">女性</td>
            <td>旭川市</td>
            <td>調査中</td>
            <td>2人</td>
        </tr>
        <tr>
            <td nowrap="nowrap">1119</td>
            <td>19004</td>
            <td nowrap="nowrap">２月２５日</td>
            <td nowrap="nowrap">非公表</td>
            <td nowrap="nowrap">非公表</td>
            <td>旭川市</td>
            <td>
            <p>No.1092</p>
            No.1093</td>
            <td>1人</td>
        </tr>
        <tr>
            <td nowrap="nowrap">1112</td>
            <td>18891</td>
            <td nowrap="nowrap">2月22日</td>
            <td nowrap="nowrap">10代未満</td>
            <td nowrap="nowrap">女性</td>
            <td>旭川市</td>
            <td>No.1074</td>
            <td>0人</td>
        </tr>
        <tr>
            <td nowrap="nowrap">1032</td>
            <td>17511</td>
            <td nowrap="nowrap">1月31日</td>
            <td nowrap="nowrap">90代</td>
            <td nowrap="nowrap">男性</td>
            <td>
            <p>旭川市</p>
            </td>
            <td>調査中</td>
            <td>8人</td>
        </tr>
        <tr>
            <th nowrap="nowrap">NO.</th>
            <th nowrap="nowrap">
            <p>北海道発表</p>
            <p>NO.</p>
            </th>
            <th nowrap="nowrap">判明日</th>
            <th nowrap="nowrap">年代</th>
            <th nowrap="nowrap">性別 </th>
            <th nowrap="nowrap">居住地</th>
            <th>周囲の患者の発生</th>
            <th>
            <p>濃厚接触者の状況</p>
            </th>
        </tr>
        <tr>
            <td nowrap="nowrap">715</td>
            <td>10716</td>
            <td nowrap="nowrap">12月9日</td>
            <td nowrap="nowrap">100代</td>
            <td nowrap="nowrap">女性</td>
            <td>旭川市</td>
            <td>あり</td>
            <td>調査中</td>
        </tr>
    </tbody>
</table>
<p><a href="test.html">新型コロナウイルス感染症の発生状況（令和3年8月19日発表分）（PDF形式90キロバイト）</a></p>
"""

    def test_content(self, html_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = html_content
        mocker.patch.object(requests, "get", return_value=responce_mock)
        html_file = DownloadedHTML("http://dummy.local")
        assert html_file.content == html_content

    def test_not_found_error(self, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 404
        mocker.patch.object(requests, "get", return_value=responce_mock)
        with pytest.raises(HTTPDownloadError, match="cannot get HTML contents."):
            DownloadedHTML("http://dummy.local")

    @pytest.mark.parametrize(
        "exception,expected",
        [
            (Timeout("Dummy Error."), "cannot connect to web server."),
            (HTTPError("Dummy Error."), "cannot connect to web server."),
            (ConnectionError("Dummy Error."), "cannot connect to web server."),
        ],
    )
    def test_network_error(self, exception, expected, mocker):
        mocker.patch.object(requests, "get", side_effect=exception)
        with pytest.raises(HTTPDownloadError, match=expected):
            DownloadedHTML("http://dummy.local")


class TestDownloadedCSV:
    @pytest.fixture()
    def csv_content(self):
        csv_content = """
No,全国地方公共団体コード,都道府県名,市区町村名,公表_年月日,発症_年月日,患者_居住地,患者_年代,患者_性別,患者_職業,患者_状態,患者_症状,患者_渡航歴の有無フラグ,患者_再陽性フラグ,患者_退院済フラグ,備考
1,10006,北海道,,2020-01-28,2020-01-21,中国武漢市,40代,女性,−,−,発熱,1,0,,海外渡航先：中国武漢
2,10006,北海道,,2020-02-14,2020-01-31,石狩振興局管内,50代,男性,自営業,−,発熱;咳;倦怠感,0,0,,
3,10006,北海道,,2020-02-19,2020-02-08,石狩振興局管内,40代,男性,会社員,−,倦怠感;筋肉痛;関節痛;発熱;咳,0,0,,
    """
        return csv_content.encode("cp932")

    def test_content(self, csv_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = csv_content
        responce_mock.headers = {"content-type": "text/csv"}
        mocker.patch.object(requests, "get", return_value=responce_mock)
        csv_file = DownloadedCSV(url="http://dummy.local", encoding="cp932")
        assert csv_file.content.getvalue() == csv_content.decode("cp932")

    def test_not_found_error(self, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 404
        mocker.patch.object(requests, "get", return_value=responce_mock)
        with pytest.raises(HTTPDownloadError, match="cannot get CSV contents."):
            DownloadedCSV("http://dummy.local")

    @pytest.mark.parametrize(
        "exception,expected",
        [
            (Timeout("Dummy Error."), "cannot connect to web server."),
            (HTTPError("Dummy Error."), "cannot connect to web server."),
            (ConnectionError("Dummy Error."), "cannot connect to web server."),
        ],
    )
    def test_network_error(self, exception, expected, mocker):
        mocker.patch.object(requests, "get", side_effect=exception)
        with pytest.raises(HTTPDownloadError, match=expected):
            DownloadedCSV("http://dummy.local")


class TestDownloadedPDF:
    def test_not_found_error(self, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 404
        mocker.patch.object(requests, "get", return_value=responce_mock)
        with pytest.raises(HTTPDownloadError, match="cannot get PDF contents."):
            DownloadedPDF("http://dummy.local")

    @pytest.mark.parametrize(
        "exception,expected",
        [
            (Timeout("Dummy Error."), "cannot connect to web server."),
            (HTTPError("Dummy Error."), "cannot connect to web server."),
            (ConnectionError("Dummy Error."), "cannot connect to web server."),
        ],
    )
    def test_network_error(self, exception, expected, mocker):
        mocker.patch.object(requests, "get", side_effect=exception)
        with pytest.raises(HTTPDownloadError, match=expected):
            DownloadedPDF("http://dummy.local")


class TestDownloadedJSON:
    @pytest.fixture()
    def json_content(self):
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

    def test_content(self, json_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = json_content
        responce_mock.headers = {"content-type": "application/json"}
        mocker.patch.object(requests, "get", return_value=responce_mock)
        json_file = DownloadedJSON("http://dummy.local")
        assert json_file.content == json.loads(json_content)

    def test_not_found_error(self, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 404
        mocker.patch.object(requests, "get", return_value=responce_mock)
        with pytest.raises(HTTPDownloadError, match="cannot get JSON contents."):
            DownloadedJSON("http://dummy.local")

    @pytest.mark.parametrize(
        "exception,expected",
        [
            (Timeout("Dummy Error."), "cannot connect to web server."),
            (HTTPError("Dummy Error."), "cannot connect to web server."),
            (ConnectionError("Dummy Error."), "cannot connect to web server."),
        ],
    )
    def test_network_error(self, exception, expected, mocker):
        mocker.patch.object(requests, "get", side_effect=exception)
        with pytest.raises(HTTPDownloadError, match=expected):
            DownloadedJSON("http://dummy.local")
