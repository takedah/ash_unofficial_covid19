import os


class Config:
    """パッケージ全体で使用する定数をまとめる"""

    # 旭川市の人口（2021年1月1日現在）
    POPULATION = 331397

    # 札幌市の人口（2021年1月1日現在）
    SAPPORO_POPULATION = 1961575

    # 旭川市公式ホームページと北海道オープンデータポータルの設定
    DATABASE_URL = os.environ.get("DATABASE_URL")
    BASE_URL = "https://www.city.asahikawa.hokkaido.jp/"
    OVERVIEW_URL = BASE_URL + "kurashi/135/136/150/d068529.html"
    LATEST_DATA_URL = BASE_URL + "kurashi/135/136/150/d073984.html"
    SEP2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073824.html"
    AUG2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073650.html"
    JUL2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073498.html"
    JUN2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073303.html"
    MAY2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073196.html"
    APR2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073132.html"
    MAR2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072959.html"
    FEB2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072703.html"
    JAN2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072504.html"
    DEC2020_DATA_URL = BASE_URL + "kurashi/135/136/150/d072337.html"
    NOV2020_OR_EARLIER_URL = BASE_URL + "kurashi/135/136/150/d072303.html"
    PDF_URL = BASE_URL + "kurashi/135/146/149/d072466_d/fil/iryoukikan.pdf"
    MEDICAL_INSTITUTIONS_URL = BASE_URL + "kurashi/135/146/149/d073389.html"
    RESERVATION_STATUSES_URL = BASE_URL + "kurashi/135/146/149/d072466_d/fil/" + "yoyakuzyoukyou.pdf"

    # 北海道オープンデータポータルの設定
    HOKKAIDO_URL = (
        "https://www.harp.lg.jp/opendata/dataset/" + "1369/resource/3132/010006_hokkaido_covid19_patients.csv"
    )

    # DATA-SMART CITY SAPPOROの設定
    SAPPORO_URL = (
        "https://ckan.pf-sapporo.jp/dataset/"
        + "c89f65e7-45a8-4ab2-b94d-494ae192c70f/resource/"
        + "b83606f6-3aa2-4e0c-8a1a-509dd36be2ae/download/patients_summary.csv"
    )

    # Yahoo! Open Local Platformの設定
    YOLP_BASE_URL = "https://map.yahooapis.jp/search/local/V1/localSearch"
    YOLP_APP_ID = os.environ.get("YOLP_APP_ID")

    # Google Analyticsの設定
    GTAG_ID = os.environ.get("GTAG_ID")
