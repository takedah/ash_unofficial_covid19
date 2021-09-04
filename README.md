# 旭川市新型コロナウイルス感染症非公式オープンデータ

## Description

北海道全体の新型コロナウイルス感染症の情報については、 [北海道新型コロナウイルスまとめサイト](https://stopcovid19.hokkaido.dev/) や [北海道オープンデータポータル](https://www.harp.lg.jp/opendata/) でCSV形式のテキストファイルやJSON形式のWeb APIといった再利用しやすい形式で取得できますが、旭川市単独のデータは [旭川市公式ホームページ](https://www.city.asahikawa.hokkaido.jp/kurashi/135/136/150/d068529.html) に掲載はあるものの、再利用しやすい形式とはなっていないのが現状です。

そこで、旭川市公式ホームページからスクレイピングして新型コロナウイルス感染症の情報を取得し、新型コロナウイルス感染症対策に関するオープンデータ項目定義書のうち、陽性患者属性データセットに基づいたCSV形式のテキストファイルを、非公式のオープンデータとしてダウンロードできるようにしたWebアプリです。Flaskで動作します。

ただし、以下のデータ項目は旭川市公式ホームページからスクレイピングで取得することが困難だったため、北海道オープンデータポータルの陽性患者属性CSVから値を逆輸入？して取得しています。（北海道オープンデータポータルの陽性患者属性CSVの更新が2021年6月19日で停止したため、同日以降以下のデータは全て空にしています。）

| No.   | Item                    |
|:-----:|:-----------------------:|
| No.6  | 発症_年月日             |
| No.10 | 患者_職業               |
| No.11 | 患者_状態               |
| No.12 | 患者_症状               |
| No.13 | 患者_渡航歴の有無フラグ |

また、旭川市内の新型コロナワクチン接種医療機関の一覧（16歳以上）を試験的にCSVファイルでダウンロードできるようにしています。

## Requirement

- PostgreSQL
- Java Runtime (8 or later)
- BeautifulSoup4
- flask
- Flask-Caching
- gunicorn
- psycopg2
- requests
- matplotlib
- pandas
- tabula-py

## Install

```bash
$ export DATABASE_URL=postgresql://{user_name}:{password}@{host_name}/{db_name}
$ psql -f db/schema.sql -U {user_name} -d {db_name} -h {host_name}
$ make init
```

Google Analyticsを使う場合、gtag_idを環境変数にセットします。

```bash
$ export GTAG_ID={google_analytics_id}
```

## Usage

```bash
$ gunicorn ash_unofficial_covid19.run:app
```

## Lisence

Copyright (c) 2021 Hiroki Takeda
[MIT](http://opensource.org/licenses/mit-license.php)
