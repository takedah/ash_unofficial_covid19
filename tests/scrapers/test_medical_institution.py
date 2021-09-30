import pytest
import requests

from ash_unofficial_covid19.scrapers.medical_institution import (
    ScrapeMedicalInstitutions,
)


@pytest.fixture()
def html_content():
    return """
<table cellspacing="0" cellpadding="0">
    <caption>新型コロナワクチン接種医療機関 </caption>
    <colgroup><col /><col /><col /><col span="2" /></colgroup>
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
            <td>
            <p>76-9838</p>
            <p>予約専用</P>
            </td>
            <td>○</td>
            <td>○備考テスト</td>
        </tr>
        <tr>
            <th>大成</th>
        </tr>
        <tr>
            <td>道北勤医協<br />

            一条通病院</td>
            <td>東光1の1</td>
            <td>
            <p>34-0015</p>

            <p>予約専用</p>

            </td>
            <td>○※1</td>
            <td>－</td>
        </tr>
        <tr>
            <th>

            <p>※1　道北勤医協一条通病院及び道北勤医協一条クリニックは、予約専用番号(34-0015)に変更となります。</p>

            <p>開始時期は、各医療機関のホームページ及び院内掲示をご覧ください。</p>

            </th>
        </tr>
    </tbody>
</table>
"""


@pytest.fixture()
def pediatric_html_content():
    return """
<table cellspacing="1" cellpadding="1">
    <caption>新型コロナワクチン接種医療機関（12歳から15歳）</caption>
    <tbody>
        <tr>
            <td>医療機関名</td>
            <td>住所</td>
            <td>電話</td>
            <td>かかりつけ医療機関</td>
            <td>コールセンター、インターネット受付</td>
        </tr>
        <tr>
            <td colspan="5">
                <a id="22" name="22"></a><strong>東・金星町・各条17～26丁目</strong>
            </td>
        </tr>
        <tr>
            <td>市立旭川病院</td>
            <td>金星町1</td>
            <td>29-0202</td>
            <td>○</td>
            <td>－</td>
        </tr>
        <tr>
            <td colspan="5">
                <a id="23" name="23"></a><strong>花咲町・末広・末広東・永山</strong>
            </td>
        </tr>
        <tr>
            <td>
               <p>独立行政法人国立病院機構</p>
               <p>旭川医療センター</p>
            </td>
            <td>花咲町7</td>
            <td>
            <p>51-3910</p>
            <p>予約専用</P>
            </td>
            <td>○</td>
            <td>ー</td>
        </tr>
    </tbody>
</table>
"""


def test_lists(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    scraper = ScrapeMedicalInstitutions(
        html_url="http://dummy.local", is_pediatric=False
    )
    expect = [
        {
            "name": "市立旭川病院",
            "address": "旭川市金星町1",
            "phone_number": "0166-29-0202",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "新富・東・金星町",
            "memo": "",
            "target_age": "16歳以上",
        },
        {
            "name": "旭川赤十字病院",
            "address": "旭川市曙1の1",
            "phone_number": "0166-76-9838 予約専用",
            "book_at_medical_institution": True,
            "book_at_call_center": True,
            "area": "西地区",
            "memo": "備考テスト",
            "target_age": "16歳以上",
        },
        {
            "name": "道北勤医協一条通病院",
            "address": "旭川市東光1の1",
            "phone_number": "0166-34-0015 予約専用",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "大成",
            "memo": (
                "道北勤医協一条通病院及び道北勤医協一条クリニックは、"
                + "予約専用番号(34-0015)に変更となります。 開始時期は、"
                + "各医療機関のホームページ及び院内掲示をご覧ください。"
            ),
            "target_age": "16歳以上",
        },
    ]
    assert scraper.lists == expect


def test_pediatric_lists(pediatric_html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = pediatric_html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    scraper = ScrapeMedicalInstitutions(
        html_url="http://dummy.local", is_pediatric=True
    )
    expect = [
        {
            "name": "市立旭川病院",
            "address": "旭川市金星町1",
            "phone_number": "0166-29-0202",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "東・金星町・各条17～26丁目",
            "memo": "",
            "target_age": "12歳から15歳まで",
        },
        {
            "name": "独立行政法人国立病院機構旭川医療センター",
            "address": "旭川市花咲町7",
            "phone_number": "0166-51-3910 予約専用",
            "book_at_medical_institution": True,
            "book_at_call_center": False,
            "area": "花咲町・末広・末広東・永山",
            "memo": "",
            "target_age": "12歳から15歳まで",
        },
    ]
    assert scraper.lists == expect


def test_get_name_lists(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    scraper = ScrapeMedicalInstitutions(
        html_url="http://dummy.local", is_pediatric=False
    )
    expect = [("市立旭川病院", "16歳以上"), ("旭川赤十字病院", "16歳以上"), ("道北勤医協一条通病院", "16歳以上")]
    name_lists = scraper.get_name_lists()
    assert name_lists == expect
