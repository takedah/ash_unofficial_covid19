import os


class Config:
    DATABASE_URL = os.environ.get("DATABASE_URL")
    BASE_URL = "https://www.city.asahikawa.hokkaido.jp/"
    LATEST_DATA_URL = BASE_URL + "kurashi/135/136/150/d068529.html"
    MAR2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072959.html"
    FEB2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072703.html"
    JAN2021_DATA_URL = BASE_URL + "kurashi/135/136/150/d072504.html"
    DEC2020_DATA_URL = BASE_URL + "kurashi/135/136/150/d072337.html"
    NOV2020_OR_EARLIER_URL = BASE_URL + "kurashi/135/136/150/d072303.html"
    HOKKAIDO_URL = (
        "https://www.harp.lg.jp/opendata/dataset/"
        + "1369/resource/3132/010006_hokkaido_covid19_patients.csv"
    )
