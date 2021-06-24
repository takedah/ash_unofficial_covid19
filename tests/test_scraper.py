import unittest
from datetime import date
from unittest.mock import Mock, patch

import pandas as pd
from requests import HTTPError, Timeout

from ash_unofficial_covid19.errors import HTTPDownloadError
from ash_unofficial_covid19.scraper import (
    DownloadedHTML,
    DownloadedPDF,
    ScrapedCSVData,
    ScrapedHTMLData,
    ScrapedMedicalInstitutionsHTMLData,
    ScrapedPDFData
)


def html_content():
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
    """


def csv_content():
    csv_data = """
No,全国地方公共団体コード,都道府県名,市区町村名,公表_年月日,発症_年月日,患者_居住地,患者_年代,患者_性別,患者_職業,患者_状態,患者_症状,患者_渡航歴の有無フラグ,患者_再陽性フラグ,患者_退院済フラグ,備考
1,10006,北海道,,2020-01-28,2020-01-21,中国武漢市,40代,女性,−,−,発熱,1,0,,海外渡航先：中国武漢
2,10006,北海道,,2020-02-14,2020-01-31,石狩振興局管内,50代,男性,自営業,−,発熱;咳;倦怠感,0,0,,
3,10006,北海道,,2020-02-19,2020-02-08,石狩振興局管内,40代,男性,会社員,−,倦怠感;筋肉痛;関節痛;発熱;咳,0,0,,
"""
    return csv_data.encode("cp932")


def medical_institution_html_content():
    html_data = """
<table cellspacing="0" cellpadding="0">
    <caption>新型コロナワクチン接種医療機関一覧 </caption>
    <tbody>
        <tr>
            <th>医療機関名</th>
            <th>住所</th>
            <th>電話</th>
            <th>かかりつけ医療機関</th>
            <th>コールセンター、インターネット受付</th>
        </tr>
        <tr>
            <th>新富・東・金星町</th>
        </tr>
        <tr>
            <td>市立旭川病院</td>
            <td>金星町1</td>
            <td>29-0202</td>
            <td>○</td>
            <td>－</td>
        </tr>
        <tr>
            <th>西地区</th>
        </tr>
        <tr>
            <td>旭川赤十字病院</td>
            <td>曙1の1</td>
            <td>22-8111</td>
            <td>○</td>
            <td>○</td>
        </tr>
    </tbody>
</table>
"""
    return html_data


class TestDownloadedHTML(unittest.TestCase):
    def setUp(self):
        self.html_content = html_content()

    def tearDown(self):
        pass

    @patch("ash_unofficial_covid19.scraper.requests")
    def test_content(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content
        )
        html_data = DownloadedHTML("http://dummy.local")
        result = html_data.content
        expect = self.html_content
        self.assertEqual(result, expect)

        mock_requests.get.side_effect = Timeout("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.side_effect = HTTPError("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.side_effect = ConnectionError("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            DownloadedHTML("http://dummy.local")

        mock_requests.get.return_value = Mock(status_code=404)
        with self.assertRaises(HTTPDownloadError):
            DownloadedHTML("http://dummy.local")


class TestScrapedHTMLData(unittest.TestCase):
    def setUp(self):
        self.html_content = html_content()

    def tearDown(self):
        pass

    def test_format_date(self):
        self.assertEqual(
            ScrapedHTMLData.format_date(date_string="3月6日", target_year=2021),
            date(2021, 3, 6),
        )

        # 全角数字が含まれている場合でも正しく変換する
        self.assertEqual(
            ScrapedHTMLData.format_date(date_string="３月６日", target_year=2021),
            date(2021, 3, 6),
        )

        # 日付ではない数字の場合Noneを返す
        self.assertEqual(
            ScrapedHTMLData.format_date(date_string="13月6日", target_year=2021),
            None,
        )

    def test_format_age(self):
        self.assertEqual(ScrapedHTMLData.format_age("20代"), "20代")
        self.assertEqual(ScrapedHTMLData.format_age("調査中"), "")
        self.assertEqual(ScrapedHTMLData.format_age("10代未満"), "10歳未満")
        self.assertEqual(ScrapedHTMLData.format_age("100代"), "90歳以上")

        # 全角数字が含まれている場合でも正しく変換する
        self.assertEqual(ScrapedHTMLData.format_age("２０代"), "20代")

    def test_format_sex(self):
        self.assertEqual(ScrapedHTMLData.format_sex("男性"), "男性")
        self.assertEqual(ScrapedHTMLData.format_sex("非公表"), "")
        self.assertEqual(ScrapedHTMLData.format_sex("その他"), "その他")
        self.assertEqual(ScrapedHTMLData.format_sex("women"), "")

    @patch("ash_unofficial_covid19.scraper.requests")
    def test_data_list(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content
        )
        downloaded_html = DownloadedHTML("http://dummy.local")
        # 年指定が正しくない場合エラーを返す
        with self.assertRaises(TypeError):
            ScrapedHTMLData(downloaded_html=downloaded_html, target_year=2019)

        scraper = ScrapedHTMLData(downloaded_html=downloaded_html, target_year=2021)
        expect = [
            {
                "patient_number": 1121,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 27),
                "onset_date": None,
                "residence": "旭川市",
                "age": "30代",
                "sex": "男性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 19080 周囲の患者の発生: "
                + "No.1072 No.1094 No.1107 No.1108 濃厚接触者の状況: 0人",
                "hokkaido_patient_number": 19080,
                "surrounding_status": "No.1072 No.1094 No.1107 No.1108",
                "close_contact": "0人",
            },
            {
                "patient_number": 1120,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 26),
                "onset_date": None,
                "residence": "旭川市",
                "age": "50代",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 19050 周囲の患者の発生: 調査中 濃厚接触者の状況: 2人",
                "hokkaido_patient_number": 19050,
                "surrounding_status": "調査中",
                "close_contact": "2人",
            },
            {
                "patient_number": 1119,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 25),
                "onset_date": None,
                "residence": "旭川市",
                "age": "",
                "sex": "",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 19004 周囲の患者の発生: No.1092             "
                + "No.1093 濃厚接触者の状況: 1人",
                "hokkaido_patient_number": 19004,
                "surrounding_status": "No.1092             No.1093",
                "close_contact": "1人",
            },
            {
                "patient_number": 1112,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 22),
                "onset_date": None,
                "residence": "旭川市",
                "age": "10歳未満",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 18891 周囲の患者の発生: No.1074 濃厚接触者の状況: 0人",
                "hokkaido_patient_number": 18891,
                "surrounding_status": "No.1074",
                "close_contact": "0人",
            },
            {
                "patient_number": 1032,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 1, 31),
                "onset_date": None,
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "男性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 17511 周囲の患者の発生: 調査中 濃厚接触者の状況: 8人",
                "hokkaido_patient_number": 17511,
                "surrounding_status": "調査中",
                "close_contact": "8人",
            },
            {
                "patient_number": 715,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 12, 9),
                "onset_date": None,
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表NO.: 10716 周囲の患者の発生: あり 濃厚接触者の状況: 調査中",
                "hokkaido_patient_number": 10716,
                "surrounding_status": "あり",
                "close_contact": "調査中",
            },
        ]
        self.assertEqual(scraper.patients_data, expect)

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


class TestScrapedCSVData(unittest.TestCase):
    def setUp(self):
        self.csv_content = csv_content()

    def tearDown(self):
        pass

    @patch("ash_unofficial_covid19.scraper.requests")
    def test_content(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200,
            content=self.csv_content,
            headers={"content-type": "text/csv"},
        )
        csv_data = ScrapedCSVData(url="http://dummy.local")
        result = csv_data.patients_data
        expect = [
            {
                "patient_number": 1,
                "city_code": "10006",
                "prefecture": "北海道",
                "city_name": "",
                "publication_date": date(2020, 1, 28),
                "onset_date": date(2020, 1, 21),
                "residence": "中国武漢市",
                "age": "40代",
                "sex": "女性",
                "occupation": "－",
                "status": "－",
                "symptom": "発熱",
                "overseas_travel_history": True,
                "be_discharged": None,
                "note": "海外渡航先：中国武漢",
            },
            {
                "patient_number": 2,
                "city_code": "10006",
                "prefecture": "北海道",
                "city_name": "",
                "publication_date": date(2020, 2, 14),
                "onset_date": date(2020, 1, 31),
                "residence": "石狩振興局管内",
                "age": "50代",
                "sex": "男性",
                "occupation": "自営業",
                "status": "－",
                "symptom": "発熱;咳;倦怠感",
                "overseas_travel_history": False,
                "be_discharged": None,
                "note": "",
            },
            {
                "patient_number": 3,
                "city_code": "10006",
                "prefecture": "北海道",
                "city_name": "",
                "publication_date": date(2020, 2, 19),
                "onset_date": date(2020, 2, 8),
                "residence": "石狩振興局管内",
                "age": "40代",
                "sex": "男性",
                "occupation": "会社員",
                "status": "－",
                "symptom": "倦怠感;筋肉痛;関節痛;発熱;咳",
                "overseas_travel_history": False,
                "be_discharged": None,
                "note": "",
            },
        ]
        self.assertEqual(result, expect)

        mock_requests.get.side_effect = Timeout("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            ScrapedCSVData("http://dummy.local")

        mock_requests.get.side_effect = HTTPError("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            ScrapedCSVData("http://dummy.local")

        mock_requests.get.side_effect = ConnectionError("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            ScrapedCSVData("http://dummy.local")

        mock_requests.get.return_value = Mock(status_code=404)
        with self.assertRaises(HTTPDownloadError):
            ScrapedCSVData("http://dummy.local")


class TestDownloadedPDF(unittest.TestCase):
    @patch("ash_unofficial_covid19.scraper.requests")
    def test_content(self, mock_requests):
        mock_requests.get.side_effect = Timeout("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            DownloadedPDF("http://dummy.local")

        mock_requests.get.side_effect = HTTPError("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            DownloadedPDF("http://dummy.local")

        mock_requests.get.side_effect = ConnectionError("Dummy Error.")
        with self.assertRaises(HTTPDownloadError):
            DownloadedPDF("http://dummy.local")

        mock_requests.get.return_value = Mock(status_code=404)
        with self.assertRaises(HTTPDownloadError):
            DownloadedPDF("http://dummy.local")


class TestScrapedPDFData(unittest.TestCase):
    def test_medical_institutions_data(self):
        pdf_content = pd.DataFrame(
            [
                [],
                [
                    "市立旭川病院",
                    "金星町1",
                    "29-0202",
                    "○",
                    "-",
                    "旭川医療センター",
                    "花咲町7",
                    "59-3910",
                    "○",
                    "○",
                    None,
                ],
                [
                    "旭川赤十字病院",
                    "曙町1の1",
                    "22-8111",
                    "○",
                    "○",
                    "旭川厚生病院",
                    "1の24",
                    "33-7171",
                    "○",
                    "-",
                    None,
                ],
                [],
            ],
            columns=[
                "name1",
                "address1",
                "phone_number1",
                "book_at_medical_institution1",
                "book_at_call_center1",
                "name2",
                "address2",
                "phone_number2",
                "book_at_medical_institution2",
                "book_at_call_center2",
                "null",
            ],
        )
        mock_pdf_content = Mock()
        mock_pdf_content.extracted_data = pdf_content
        scraper = ScrapedPDFData(pdf_content=mock_pdf_content)
        expect = [
            {
                "name": "市立旭川病院",
                "address": "旭川市金星町1",
                "phone_number": "0166-29-0202",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "",
            },
            {
                "name": "旭川赤十字病院",
                "address": "旭川市曙町1の1",
                "phone_number": "0166-22-8111",
                "book_at_medical_institution": True,
                "book_at_call_center": True,
                "area": "",
            },
            {
                "name": "旭川医療センター",
                "address": "旭川市花咲町7",
                "phone_number": "0166-59-3910",
                "book_at_medical_institution": True,
                "book_at_call_center": True,
                "area": "",
            },
            {
                "name": "旭川厚生病院",
                "address": "旭川市1の24",
                "phone_number": "0166-33-7171",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "",
            },
        ]
        self.assertEqual(scraper.medical_institutions_data, expect)


class TestScrapedMedicalInstitutionsHTMLData(unittest.TestCase):
    def setUp(self):
        self.html_content = medical_institution_html_content()

    def tearDown(self):
        pass

    @patch("ash_unofficial_covid19.scraper.requests")
    def test_items(self, mock_requests):
        mock_requests.get.return_value = Mock(
            status_code=200, content=self.html_content
        )
        downloaded_html = DownloadedHTML("http://dummy.local")
        scraper = ScrapedMedicalInstitutionsHTMLData(downloaded_html=downloaded_html)
        expect = [
            {
                "name": "市立旭川病院",
                "address": "旭川市金星町1",
                "phone_number": "0166-29-0202",
                "book_at_medical_institution": True,
                "book_at_call_center": False,
                "area": "新富・東・金星町",
            },
            {
                "name": "旭川赤十字病院",
                "address": "旭川市曙1の1",
                "phone_number": "0166-22-8111",
                "book_at_medical_institution": True,
                "book_at_call_center": True,
                "area": "西地区",
            },
        ]
        self.assertEqual(scraper.items, expect)


if __name__ == "__main__":
    unittest.main()
