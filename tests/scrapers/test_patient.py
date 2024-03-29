from datetime import date

import pandas as pd
import pytest
import requests
from numpy import nan

from ash_unofficial_covid19.errors import ScrapeError
from ash_unofficial_covid19.scrapers.patient import (
    ScrapeAsahikawaPatients,
    ScrapeAsahikawaPatientsPDF,
    ScrapeHokkaidoPatients,
)


class TestScrapeAsahikawaPatients:
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

    def test_lists(self, html_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = html_content
        mocker.patch.object(requests, "get", return_value=responce_mock)
        scraper = ScrapeAsahikawaPatients(html_url="http://dummy.local", target_year=2021)
        expect = [
            {
                "patient_number": 1121,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 28),
                "onset_date": None,
                "residence": "旭川市",
                "age": "30代",
                "sex": "男性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表No.;19080;周囲の患者の発生;No.1072 No.1094 No.1107 No.1108;濃厚接触者の状況;0人;",
                "hokkaido_patient_number": 19080,
                "surrounding_status": "No.1072 No.1094 No.1107 No.1108",
                "close_contact": "0人",
            },
            {
                "patient_number": 1120,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 27),
                "onset_date": None,
                "residence": "旭川市",
                "age": "50代",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表No.;19050;周囲の患者の発生;調査中;濃厚接触者の状況;2人;",
                "hokkaido_patient_number": 19050,
                "surrounding_status": "調査中",
                "close_contact": "2人",
            },
            {
                "patient_number": 1119,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 26),
                "onset_date": None,
                "residence": "旭川市",
                "age": "",
                "sex": "",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表No.;19004;周囲の患者の発生;No.1092 No.1093;濃厚接触者の状況;1人;",
                "hokkaido_patient_number": 19004,
                "surrounding_status": "No.1092 No.1093",
                "close_contact": "1人",
            },
            {
                "patient_number": 1112,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 23),
                "onset_date": None,
                "residence": "旭川市",
                "age": "10歳未満",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表No.;18891;周囲の患者の発生;No.1074;濃厚接触者の状況;0人;",
                "hokkaido_patient_number": 18891,
                "surrounding_status": "No.1074",
                "close_contact": "0人",
            },
            {
                "patient_number": 1032,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 2, 1),
                "onset_date": None,
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "男性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表No.;17511;周囲の患者の発生;調査中;濃厚接触者の状況;8人;",
                "hokkaido_patient_number": 17511,
                "surrounding_status": "調査中",
                "close_contact": "8人",
            },
            {
                "patient_number": 715,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 12, 10),
                "onset_date": None,
                "residence": "旭川市",
                "age": "90歳以上",
                "sex": "女性",
                "occupation": "",
                "status": "",
                "symptom": "",
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表No.;10716;周囲の患者の発生;あり;濃厚接触者の状況;調査中;",
                "hokkaido_patient_number": 10716,
                "surrounding_status": "あり",
                "close_contact": "調査中",
            },
        ]
        assert scraper.lists == expect

    def test_unexpect_table(self, mocker):
        dummy_table = """
        <table>
          <tbody>
            <tr>
              <td>this</td><td>is</td><td>dummy</td>
            </tr>
          </tbody>
        </table>
        """
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = dummy_table
        mocker.patch.object(requests, "get", return_value=responce_mock)
        scraper = ScrapeAsahikawaPatients(html_url="http://dummy.local", target_year=2021)
        assert scraper.lists == []

    def test_target_year_error(self, html_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = html_content
        mocker.patch.object(requests, "get", return_value=responce_mock)
        with pytest.raises(ScrapeError, match="対象年の指定が正しくありません。"):
            ScrapeAsahikawaPatients(html_url="http://dummy.local", target_year=2019)


class TestScrapeHokkaidoPatients:
    @pytest.fixture()
    def csv_content(self):
        csv_content = """
    No,全国地方公共団体コード,都道府県名,市区町村名,公表_年月日,発症_年月日,患者_居住地,患者_年代,患者_性別,患者_職業,患者_状態,患者_症状,患者_渡航歴の有無フラグ,患者_再陽性フラグ,患者_退院済フラグ,備考
    1,10006,北海道,,2020-01-28,2020-01-21,中国武漢市,40代,女性,−,−,発熱,1,0,,海外渡航先：中国武漢
    2,10006,北海道,,2020-02-14,2020-01-31,石狩振興局管内,50代,男性,自営業,−,発熱;咳;倦怠感,0,0,,
    3,10006,北海道,,2020-02-19,2020-02-08,石狩振興局管内,40代,男性,会社員,−,倦怠感;筋肉痛;関節痛;発熱;咳,0,0,,
    """
        return csv_content.encode("cp932")

    def test_lists(self, csv_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = csv_content
        responce_mock.headers = {"content-type": "text/csv"}
        mocker.patch.object(requests, "get", return_value=responce_mock)
        csv_data = ScrapeHokkaidoPatients("http://dummy.local")
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
        assert csv_data.lists == expect


class TestScrapeAsahikawaPatientsPDF:
    @pytest.fixture()
    def pdf_dataframe(self):
        df1 = pd.DataFrame([[]])
        df2 = pd.DataFrame(
            [
                [
                    nan,
                    "市内番号",
                    "道内番号",
                    "国籍",
                    "居住地",
                    "年代",
                    "性別",
                    "職業等",
                    "リンク",
                    "濃厚接触者",
                ],
                [1.0, "6", "66", "日本", "旭川市", "40代", "男性", "非公表", "有り", "3人"],
            ]
        )
        return [df1, df2]

    def test_lists(self, pdf_dataframe, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = "".encode("utf-8")
        responce_mock.headers = {"content-type": "application/pdf"}
        mocker.patch.object(requests, "get", return_value=responce_mock)
        mocker.patch.object(ScrapeAsahikawaPatientsPDF, "_get_dataframe", return_value=pdf_dataframe)
        scraper = ScrapeAsahikawaPatientsPDF(pdf_url="http://dummy.local", publication_date=date(2021, 8, 19))
        expect = [
            {
                "patient_number": 6,
                "city_code": "012041",
                "prefecture": "北海道",
                "city_name": "旭川市",
                "publication_date": date(2021, 8, 19),
                "onset_date": None,
                "residence": "旭川市",
                "age": "40代",
                "sex": "男性",
                "occupation": "非公表",
                "status": None,
                "symptom": None,
                "overseas_travel_history": None,
                "be_discharged": None,
                "note": "北海道発表No.;66;周囲の患者の発生;有り;濃厚接触者の状況;3人;",
                "hokkaido_patient_number": 66,
                "surrounding_status": "有り",
                "close_contact": "3人",
            },
        ]
        assert scraper.lists == expect
