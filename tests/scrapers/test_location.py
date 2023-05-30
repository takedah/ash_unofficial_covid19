import pytest
import requests

from ash_unofficial_covid19.scrapers.location import ScrapeOpendataLocation, ScrapeYOLPLocation


class TestScrapeYOLPLocation:
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

    def test_lists(self, json_content, mocker):
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


class TestScrapeOpendataLocation:
    @pytest.fixture()
    def csv_content(self):
        csv_content = """
都道府県コード又は市区町村コード,No,都道府県名,振興局,市町村,名称,名称_カナ,医療機関の種類,郵便番号,所在地,方書,緯度,経度,電話番号,内線番号,FAX番号,法人番号,開設者氏名,管理者氏名,指定年月日,登録理由,指定期間開始,医療機関コード,診療曜日,診療開始時間,診療終了時間,診療日時特記事項,時間外における対応,診療科目,病床数,療養病床,特定機能,現存・休止,URL,備考,緯度経度出典,データ作成日
010006,287,北海道,上川総合振興局,旭川市,市立旭川病院,,病院,070-0029,旭川市金星町１丁目１番６５号,,43.778144,142.365952,0166-24-3181,,,,旭川市,石井　良直,昭32. 7. 1,新規,平29. 7. 1,2910997,,,,,,内;外;耳い;産婦;小;皮;眼;整外;精;放;ひ;麻;神内;呼;消;循;心外;呼外;病理;歯外,481,,,現存,,,地理院地図,2022-11-23
010006,19,北海道,石狩振興局,札幌市,市立札幌病院,,病院,060-8604,札幌市中央区北１１条西１３丁目１番１号,,43.07099935,141.3346474,011-726-2211,,,,札幌市,西川　秀司,平7. 10. 5,移動,令4. 10. 5,0116381,,,,,,呼内;消化器内科;循環器内科;腎臓内科;糖尿病・内分泌内科;血液内科;新生児内科;感染症内科;緩和ケア内科;リウマチ・免疫内科;脳内;小;外科;乳腺外科;腎臓移植外科;整外;形外;脳外;呼外;心外;皮;ひ;産婦;眼;耳鼻咽喉科・甲状腺外科;リハ;放射線治療科;放射線診断科;麻;歯外;精;病理;救急科,672,,,現存,,,地理院地図,2022-11-23
010006,286,北海道,上川総合振興局,旭川市,旭川赤十字病院,,病院,070-8530,旭川市曙１条１丁目１番１号,,43.769637,142.348394,0166-22-8111,,,,日本赤十字社,牧野　憲一,昭32. 8. 14,新規,平29. 8. 14,2910062,,,,,,内;呼内;消;循;救命;病理;精;小;脳内;産婦;外;整外;脳外;心外;呼外;眼;耳い;ひ;形外;皮;リハ;麻;放;歯外,520,,,現存,,,地理院地図,2022-11-23
010006,298,北海道,上川総合振興局,旭川市,ＪＡ北海道厚生連　旭川厚生病院,,病院,078-8211,旭川市１条通２４丁目１１１番地３,,43.758732,142.384931,0166-33-7171,,,,北海道厚生農業協同組合連合会,森　逹也,昭63. 3. 30,移動,平30. 3. 30,2914577,,,,,,内;精;消;循;小;外;整外;形外;呼外;皮;ひ;産婦;眼;耳い;リハ;放;麻;神内;呼;病理,460,,,現存,,,地理院地図,2022-11-23
"""
        return csv_content.encode("shift_jis")

    def test_lists(self, csv_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.content = csv_content
        responce_mock.headers = {"content-type": "text/csv"}
        mocker.patch.object(requests, "get", return_value=responce_mock)
        location_data = ScrapeOpendataLocation("http://dummy.local")
        result = location_data.lists
        expect = [
            {
                "medical_institution_name": "市立旭川病院",
                "longitude": 142.365952,
                "latitude": 43.778144,
            },
            {
                "medical_institution_name": "旭川赤十字病院",
                "longitude": 142.348394,
                "latitude": 43.769637,
            },
            {
                "medical_institution_name": "JA北海道厚生連旭川厚生病院",
                "longitude": 142.384931,
                "latitude": 43.758732,
            },
        ]
        assert expect == result
