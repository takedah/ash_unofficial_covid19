import pytest
import requests

from ash_unofficial_covid19.scrapers.outpatient_link import ScrapeOutpatientLink


class TestScrapeOutpatientLink:
    @pytest.fixture()
    def html_content(self):
        return """
<article class="body">
    <div class="ss-alignment ss-alignment-flow">
        <h3>「外来対応医療機関（発熱外来）」及び「陽性者（療養者）の治療に関与する医療機関」</h3>
    </div>
    <div class="ss-alignment ss-alignment-flow">
        <script src="https://www.pref.hokkaido.lg.jp/js/float.js"></script>
        <link rel="stylesheet" href="https://www.pref.hokkaido.lg.jp/css/float.css" />
    </div>
    <div class="ss-alignment ss-alignment-float">
        <p><a href="/fs/8/6/1/1/8/9/3/_/%E3%80%90%E6%9C%AD%E5%B9%8C%E5%B8%82%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).pdf"
                target="_blank"><img alt="01P_札幌.jpg" src="/fs/8/4/9/5/8/5/2/_/01P_%E6%9C%AD%E5%B9%8C.jpg" /></a>
        </p>
    </div>
    <div class="ss-alignment ss-alignment-child">
        <p><a href="/fs/8/6/1/0/4/0/9/_/%E3%80%90%E6%9C%AD%E5%B9%8C%E5%B8%82%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).xlsx"
                target="_blank"><img alt="01E_札幌市.jpg"
                    src="/fs/8/4/9/5/8/5/5/_/01E_%E6%9C%AD%E5%B9%8C%E5%B8%82.jpg" /></a></p>
    </div>
    <div class="ss-alignment ss-alignment-child">
        <p><a href="/fs/8/6/1/1/8/9/2/_/%E3%80%90%E9%81%93%E5%A4%AE%E5%9C%B0%E5%9F%9F%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).pdf"
                target="_blank"><img alt="05P_道央地域.jpg"
                    src="/fs/8/4/9/5/8/5/8/_/05P_%E9%81%93%E5%A4%AE%E5%9C%B0%E5%9F%9F.jpg" /></a>
        </p>
    </div>
    <div class="ss-alignment ss-alignment-child">
        <p><a href="/fs/8/6/1/0/4/1/1/_/%E3%80%90%E9%81%93%E5%A4%AE%E5%9C%B0%E5%9F%9F%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).xlsx"
                target="_blank"><img alt="05E_道央地域.jpg"
                    src="/fs/8/4/9/5/8/6/1/_/05E_%E9%81%93%E5%A4%AE%E5%9C%B0%E5%9F%9F.jpg" /></a>
        </p>
    </div>
    <div class="ss-alignment ss-alignment-child">
        <p><a href="https://www.google.com/maps/d/edit?mid=1dsFPoVjnGg-65yqbtHEqDwjmogNWMN0&amp;usp=sharing"><img
                    alt="外来対応医療機関（いわゆる発熱外来）のマップはこちらをご覧ください。" src="/fs/8/4/9/5/8/6/4/_/%E5%9B%B31-2.png" /></a></p>
    </div>
    <div class="ss-alignment ss-alignment-float">
        <p><a href="/fs/8/6/1/1/8/9/1/_/%E3%80%90%E6%97%AD%E5%B7%9D%E5%B8%82%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).pdf"
                target="_blank"><img alt="02P_旭川.jpg" src="/fs/8/4/9/5/8/6/6/_/02P_%E6%97%AD%E5%B7%9D.jpg" /></a>
        </p>
    </div>
    <div class="ss-alignment ss-alignment-child">
        <p><a href="/fs/8/6/1/1/7/8/8/_/%E3%80%90%E6%97%AD%E5%B7%9D%E5%B8%82%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).xlsx"
                target="_blank"><img alt="02E_旭川.jpg" src="/fs/8/4/9/5/8/6/9/_/02E_%E6%97%AD%E5%B7%9D.jpg" /></a>
        </p>
    </div>
    <div class="ss-alignment ss-alignment-child">
        <p><a href="/fs/8/6/1/1/8/9/0/_/%E3%80%90%E9%81%93%E5%8D%97%E5%9C%B0%E5%9F%9F%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).pdf"
                target="_blank"><img alt="06P_道南地域.jpg"
                    src="/fs/8/4/9/5/8/7/2/_/06P_%E9%81%93%E5%8D%97%E5%9C%B0%E5%9F%9F.jpg" /></a>
        </p>
    </div>
</article>
"""

    def test_lists(self, html_content, mocker):
        responce_mock = mocker.Mock()
        responce_mock.status_code = 200
        responce_mock.headers = {"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}
        responce_mock.content = html_content
        mocker.patch.object(requests, "get", return_value=responce_mock)
        scraper = ScrapeOutpatientLink(html_url="http://dummy.local")
        expect = [
            {
                "url": "https://www.pref.hokkaido.lg.jp/"
                + "fs/8/6/1/1/7/8/8/_/%E3%80%90%E6%97%AD%E5%B7%9D%E5%B8%82%E3%80%91%E5%A4%96%E6%9D%A5%E5%AF%BE%E5%BF%9C%E5%8C%BB%E7%99%82%E6%A9%9F%E9%96%A2(R5.6.7).xlsx",
            },
        ]
        assert scraper.lists == expect
