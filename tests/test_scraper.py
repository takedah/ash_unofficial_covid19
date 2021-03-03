import unittest
from datetime import date
from unittest.mock import Mock, patch

from requests import HTTPError, Timeout

from ash_covid19.errors import HTMLDownloadError
from ash_covid19.scraper import DownloadedHTML, ScrapedHTMLData


def html_content1():
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
            <td nowrap="nowrap">2月26日</td>
            <td nowrap="nowrap">50代</td>
            <td nowrap="nowrap">女性</td>
            <td>旭川市</td>
            <td>調査中</td>
            <td>2人</td>
        </tr>
        <tr>
            <td nowrap="nowrap">1119</td>
            <td>19004</td>
            <td nowrap="nowrap">2月25日</td>
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
    </tbody>
</table>
    """


def html_content2():
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
    """


class TestDownloadedHTML(unittest.TestCase):
    def setUp(self):
        self.html_content1 = html_content1()

    def tearDown(self):
        pass

    @patch("ash_covid19.scraper.requests")
    def test_content(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content1
        )
        schedule_html = DownloadedHTML("http://dummy.local")
        result = schedule_html.content
        expect = self.html_content1
        self.assertEqual(result, expect)

        mock_requests.get.side_effect = Timeout("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.side_effect = HTTPError("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.side_effect = ConnectionError("Dummy Error.")
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.return_value = Mock(status_code=404)
        with self.assertRaises(HTMLDownloadError):
            DownloadedHTML("http://dummy.local")


class TestScrapedHTMLData(unittest.TestCase):
    def setUp(self):
        self.html_content1 = html_content1()
        self.html_content2 = html_content2()

    def tearDown(self):
        pass

    @patch("ash_covid19.scraper.requests")
    def test_data_list(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content1
        )
        downloaded_html = DownloadedHTML("http://dummy.local")
        scraper = ScrapedHTMLData(downloaded_html=downloaded_html, target_year=2021)
        expect1 = [
            {
                "patient_number": 1121,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 27),
                "onset_date": "",
                "residence": "旭川市",
                "age": "30代",
                "sex": "男性",
                "status": "",
                "symptom": "",
                "overseas_travel_history": "",
                "be_discharged": "",
                "note": "北海道発表NO.: 19080 周囲の患者の発生: "
                + "No.1072 No.1094 No.1107 No.1108 濃厚接触者の状況: 0人",
            },
            {
                "patient_number": 1120,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 26),
                "onset_date": "",
                "residence": "旭川市",
                "age": "50代",
                "sex": "女性",
                "status": "",
                "symptom": "",
                "overseas_travel_history": "",
                "be_discharged": "",
                "note": "北海道発表NO.: 19050 周囲の患者の発生: 調査中 濃厚接触者の状況: 2人",
            },
            {
                "patient_number": 1119,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 25),
                "onset_date": "",
                "residence": "旭川市",
                "age": "",
                "sex": "非公表",
                "status": "",
                "symptom": "",
                "overseas_travel_history": "",
                "be_discharged": "",
                "note": "北海道発表NO.: 19004 周囲の患者の発生: No.1092             "
                + "No.1093 濃厚接触者の状況: 1人",
            },
            {
                "patient_number": 1112,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 22),
                "onset_date": "",
                "residence": "旭川市",
                "age": "10歳未満",
                "sex": "女性",
                "status": "",
                "symptom": "",
                "overseas_travel_history": "",
                "be_discharged": "",
                "note": "北海道発表NO.: 18891 周囲の患者の発生: No.1074 濃厚接触者の状況: 0人",
            },
            {
                "patient_number": 1032,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 1, 31),
                "onset_date": "",
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "男性",
                "status": "",
                "symptom": "",
                "overseas_travel_history": "",
                "be_discharged": "",
                "note": "北海道発表NO.: 17511 周囲の患者の発生: 調査中 濃厚接触者の状況: 8人",
            },
        ]
        self.assertEqual(scraper.patients_data, expect1)

        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content2
        )
        downloaded_html = DownloadedHTML("http://dummy.local")
        scraper = ScrapedHTMLData(downloaded_html=downloaded_html, target_year=2020)
        expect2 = [
            {
                "patient_number": 715,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2020, 12, 9),
                "onset_date": "",
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "女性",
                "status": "",
                "symptom": "",
                "overseas_travel_history": "",
                "be_discharged": "",
                "note": "北海道発表NO.: 10716 周囲の患者の発生: あり 濃厚接触者の状況: 調査中",
            },
        ]
        self.assertEqual(scraper.patients_data, expect2)

        # 想定外のテーブル要素があった場合は空リストを返す。
        dummy_table = """
        <table>
          <tbody>
            <tr>
              <td>this</td><td>is</td><td>dummy</td>
            </tr>
          </tbody>
        </table>
        """
        mock_requests.get.return_value = Mock(status_code=200, content=dummy_table)
        downloaded_html = DownloadedHTML("http://dummy.local")
        scraper = ScrapedHTMLData(downloaded_html=downloaded_html, target_year=2021)
        self.assertEqual(scraper.patients_data, [])
