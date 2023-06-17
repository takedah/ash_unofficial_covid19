# 旭川市非公式新型コロナウイルスまとめサイト

## Description

[旭川市非公式新型コロナウイルスまとめサイト](https://covid19.asahikawa-opendata.morori.jp/)

北海道全体の新型コロナウイルス感染症の情報については、[北海道オープンデータポータル](https://www.harp.lg.jp/opendata/) でCSV形式のテキストファイルといった再利用しやすい形式で取得できますが、旭川市単独のデータは [旭川市公式ホームページ](https://www.city.asahikawa.hokkaido.jp/kurashi/135/136/150/d068529.html) に掲載はあるものの、再利用しやすい形式とはなっていないのが現状です。

そこで、旭川市公式ホームページからスクレイピングして新型コロナウイルス感染症の情報を取得し、非公式のオープンデータとしてダウンロードできるようにしたものです。（2023年5月8日発表分をもって新規感染者数データの取得は停止しています。）

また、新型コロナワクチン接種医療機関を検索したり、北海道公式ホームページからダウンロードしたデータを元に外来対応医療機関（発熱外来）を検索できるようになっています。

Flaskで動作します。

## Requirement

- PostgreSQL
- Java Runtime (8 or later)
- beautifulsoup4
- flask
- gunicorn
- psycopg2
- requests
- matplotlib
- pandas
- tabula-py
- camelot
- opencv-python
- opencv-python-headless
- ghostscript
- pillow
- pytest
- pytest-mock

## Install

新型コロナワクチン接種医療機関の位置情報の取得に [Yahoo! Open Local Platform (YOLP)](https://developer.yahoo.co.jp/webapi/map/) を使用しています。

```bash
$ export DATABASE_URL=postgresql://{user_name}:{password}@{host_name}/{db_name}
$ export YOLP_APP_ID={your_yolp_app_id}
$ psql -f db/schema.sql -U {user_name} -d {db_name} -h {host_name}
$ make init
```

Google Analyticsを使う場合、gtag_idを環境変数にセットします。

```bash
$ export GTAG_ID={google_analytics_id}
```

## Usage
### サービス起動

```bash
$ gunicorn ash_unofficial_covid19.run:app
```

### 感染者情報の取得

```bash
$ python -m ash_unofficial_covid19.import_patients_numbers
```

### ワクチン接種予約状況の取得

```bash
$ python -m ash_unofficial_covid19.import_reservation_statuses
```

### 発熱外来の情報の取得

```bash
$ python -m ash_unofficial_covid19.import_outpatients
```

### Dockerでのサービス起動

Dockerでも使用できるようにしています。

#### サービス起動

```bash
# docker-compose build
# docker-compose up -d
```

#### データ取得

```bash
# docker-compose exec app python -m ash_unofficial_covid19.import_patients_numbers
# docker-compose exec app python -m ash_unofficial_covid19.import_reservation_statuses
# docker-compose exec app python -m ash_unofficial_covid19.import_outpatients
```

#### サービス停止

```bash
# docker-compose down
```

## Lisence

Copyright (c) 2023 Hiroki Takeda
[MIT](http://opensource.org/licenses/mit-license.php)
