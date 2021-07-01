import os


class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    BASE_URL = "https://www.city.asahikawa.hokkaido.jp/"
    LATEST_DATA_URL = BASE_URL + "kurashi/135/136/150/d073498.html"
    JUN2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073303.html"
    MAY2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073196.html"
    APR2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d073132.html"
    MAR2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072959.html"
    FEB2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072703.html"
    JAN2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072504.html"
    DEC2020_DATA_URL = BASE_URL + "kurashi/135/136/150/d072337.html"
    NOV2020_OR_EARLIER_URL = BASE_URL + "kurashi/135/136/150/d072303.html"
    PDF_URL = BASE_URL + "kurashi/135/146/149/d072466_d/fil/iryoukikan.pdf"
    HOKKAIDO_URL = (
        "https://www.harp.lg.jp/opendata/dataset/"
        + "1369/resource/3132/010006_hokkaido_covid19_patients.csv"
    )
    MEDICAL_INSTITUTIONS_URL = BASE_URL + "kurashi/135/146/149/d073389.html"
    GTAG_ID = os.environ.get("GTAG_ID")
