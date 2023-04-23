import pytest
import requests

from ash_unofficial_covid19.scrapers.reservation_status import ScrapeReservationStatus


@pytest.fixture()
def html_content():
    return """
<table id="tablepress-26-no-2" class="tablepress tablepress-id-26 c-table__reservation-about">
<thead>
<tr class="row-1 odd">
<th class="column-1">地区</th>
<th class="column-2">医療機関名</th>
<th class="column-3">住所</th>
<th class="column-4"></th>
<th class="column-5">電話番号</th>
<th class="column-6">接種種類</th>
<th class="column-7">使用ワクチン</th>
<th class="column-8">受付開始</th>
<th class="column-9">接種開始</th>
<th class="column-10">かかりつけ<br />患者</th>
<th class="column-11">かかりつけ<br />患者以外</th>
<th class="column-12">市外</th>
<th class="column-13">備考</th>
</tr>
</thead>
<tbody class="row-hover">
<tr class="row-2 even">
<td class="column-1">西地区</td>
<td class="column-2">旭川赤十字病院</td>
<td class="column-3">曙1条1丁目</td>
<td class="column-4"></td>
<td class="column-5">76-9838(予約専用）</td>
<td class="column-6">春開始接種（12歳以上）</td>
<td class="column-7">モデルナ</td>
<td class="column-8">受付中</td>
<td class="column-9">2/12～</td>
<td class="column-10"></td>
<td class="column-11">×</td>
<td class="column-12">×</td>
<td class="column-13">当院ホームページをご確認ください</td>
</tr>
<tr class="row-3 odd">
<td class="column-1">花咲町・末広・末広東・東鷹栖地区</td>
<td class="column-2">独立行政法人国立病院機構旭川医療センター</td>
<td class="column-3">花咲町7丁目</td>
<td class="column-4"></td>
<td class="column-5">51-3910予約専用</td>
<td class="column-6">小児接種（３回目以降）</td>
<td class="column-7">ファイザー モデルナ</td>
<td class="column-8">受付中</td>
<td class="column-9">2/1～</td>
<td class="column-10">○</td>
<td class="column-11">×</td>
<td class="column-12"></td>
<td class="column-13"></td>
</tr>
<tr class="row-4 even">
<td class="column-1">西地区</td>
<td class="column-2">旭川赤十字病院</td>
<td class="column-3">曙1条1丁目</td>
<td class="column-4"></td>
<td class="column-5">76-9838(予約専用）</td>
<td class="column-6">小児接種（３回目以降）</td>
<td class="column-7">モデルナ</td>
<td class="column-8">受付中</td>
<td class="column-9">2/12～</td>
<td class="column-10"></td>
<td class="column-11">×※条件あり</td>
<td class="column-12">×</td>
<td class="column-13">当院ホームページをご確認ください</td>
</tr>
</tbody>
</table>
"""


def test_lists(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    scraper = ScrapeReservationStatus("http://dummy.local")
    expect = [
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "division": "春開始接種（12歳以上）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "memo": "当院ホームページをご確認ください",
        },
        {
            "area": "花咲町・末広・末広東・東鷹栖地区",
            "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
            "address": "花咲町7丁目",
            "phone_number": "51-3910予約専用",
            "division": "小児接種（３回目以降）",
            "vaccine": "ファイザー モデルナ",
            "status": "受付中",
            "inoculation_time": "2/1～",
            "is_target_family": True,
            "is_target_not_family": False,
            "is_target_suberb": None,
            "memo": "",
        },
        {
            "area": "西地区",
            "medical_institution_name": "旭川赤十字病院",
            "address": "曙1条1丁目",
            "phone_number": "76-9838(予約専用）",
            "division": "小児接種（３回目以降）",
            "vaccine": "モデルナ",
            "status": "受付中",
            "inoculation_time": "2/12～",
            "is_target_family": None,
            "is_target_not_family": False,
            "is_target_suberb": False,
            "memo": "かかりつけ患者以外は※条件あり 当院ホームページをご確認ください",
        },
    ]
    assert scraper.lists == expect


def test_get_medical_institution_list(html_content, mocker):
    responce_mock = mocker.Mock()
    responce_mock.status_code = 200
    responce_mock.content = html_content
    mocker.patch.object(requests, "get", return_value=responce_mock)
    scraper = ScrapeReservationStatus("http://dummy.local")
    expect = [("旭川赤十字病院", "春開始接種（12歳以上）"), ("独立行政法人国立病院機構旭川医療センター", "小児接種（３回目以降）"), ("旭川赤十字病院", "小児接種（３回目以降）")]
    name_lists = scraper.get_medical_institution_list()
    assert name_lists == expect
