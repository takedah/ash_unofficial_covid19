import pytest
import requests

from ash_unofficial_covid19.scrapers.first_reservation_status import ScrapeFirstReservationStatus


@pytest.fixture()
def html_content():
    return """
<table id="tablepress-1-no-2" class="tablepress tablepress-id-1">
<thead>
<tr class="row-1 odd">
<th class="column-1">地区</th><th class="column-2">医療機関名<br />
住　　所<br />
電話番号</th>
<th class="column-3">接種する<br />
ワクチン</th>
<th class="column-4">予約受付開始時期</th>
<th class="column-5">接種可能時期</th>
<th class="column-6">年　齢</th>
<th class="column-7">かかりつけ<br />
</th><th class="column-8">かかりつけ<br />
以外</th>
<th class="column-9">その他</th><th class="column-10">備考</th>
</tr>
</thead>
<tbody class="row-hover">
<tr class="row-12 even">
<td class="column-1">西地区</td><td class="column-2">旭川赤十字病院<br />
曙1条1丁目<br />
76-9838(予約専用）</td>
<td class="column-3">モデルナ</td>
<td class="column-4">受付中</td>
<td class="column-5">2/12～</td>
<td class="column-6">―</td>
<td class="column-7">×</td>
<td class="column-8">×</td>
<td class="column-9">当院の患者IDをお持ちの方</td>
<td class="column-10">当院ホームページをご確認ください</td>
</tr>
<tr class="row-68 even">
<td class="column-1">花咲町・末広・末広東・東鷹栖地区</td>
<td class="column-2">独立行政法人国立病院機構<br />
旭川医療センター<br />
花咲町7丁目<br />
51-3910予約専用</td>
<td class="column-3">ファイザー<br />
モデルナ</td>
<td class="column-4">受付中</td>
<td class="column-5">2/1～</td>
<td class="column-6">18歳以上</td>
<td class="column-7">○</td>
<td class="column-8">×</td>
<td class="column-9">―</td>
<td class="column-10"></td>
</tr>
</tbody>
</table>
<table id="tablepress-2-no-2" class="tablepress tablepress-id-2">
<thead>
<tr class="row-1 odd">
<th class="column-1">地区</th><th class="column-2">医療機関名<br />
住　　所<br />
電話番号</th>
<th class="column-3">予約受付状況</th>
<th class="column-4">接種可能時期</th>
<th class="column-5">年　齢</th>
<th class="column-6">かかりつけ</th>
<th class="column-7">かかりつけ<br />
以外</th>
<th class="column-8">市外可</th>
<th class="column-9">その他</th>
<th class="column-10">備考</th>
</tr>
</thead>
<tbody class="row-hover">
<tr class="row-36 even">
<td class="column-1">新富・東・金星町地区</td><td class="column-2">市立旭川病院<br />
金星町1丁目<br />
29-0202予約専用</td>
<td class="column-3">―</td>
<td class="column-4">―</td>
<td class="column-5">―</td>
<td class="column-6">―</td>
<td class="column-7">―</td>
<td class="column-8">―</td>
<td class="column-9">―</td>
<td class="column-10"></td>
</tr>
<tr class="row-31 odd">
<td class="column-1">各条１７～２６丁目・宮前・南地区</td><td class="column-2">森山病院<br />
宮前2条1丁目<br />
45-2026予約専用</td>
<td class="column-3">受付中</td>
<td class="column-4">2月28日～8月</td>
<td class="column-5">18歳以上</td>
<td class="column-6">○</td>
<td class="column-7">×</td>
<td class="column-8">○</td>
<td class="column-9"></td>
<td class="column-10">月・水　14:00～15:00</td>
</tr>
</tbody>
</table>
"""


def test_lists(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    scraper = ScrapeFirstReservationStatus("http://dummy.local")
    expect = [
        {
            "area": "新富・東・金星町地区",
            "medical_institution_name": "市立旭川病院",
            "address": "金星町1丁目",
            "phone_number": "29-0202予約専用",
            "vaccine": None,
            "status": "",
            "inoculation_time": "",
            "target_age": "",
            "is_target_family": None,
            "is_target_not_family": None,
            "is_target_suberb": None,
            "target_other": "",
            "memo": "",
        },
        {
            "area": "各条１７～２６丁目・宮前・南地区",
            "medical_institution_name": "森山病院",
            "address": "宮前2条1丁目",
            "phone_number": "45-2026予約専用",
            "vaccine": None,
            "status": "受付中",
            "inoculation_time": "2月28日～8月",
            "target_age": "18歳以上",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": True,
            "target_other": "",
            "memo": "月・水 14:00～15:00",
        },
    ]
    assert scraper.lists == expect


def test_get_medical_institution_list(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    scraper = ScrapeFirstReservationStatus("http://dummy.local")
    expect = ["市立旭川病院", "森山病院"]
    name_lists = scraper.get_medical_institution_list()
    assert name_lists == expect
