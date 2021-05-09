from io import BytesIO

import pandas as pd
import requests
import tabula

from ash_unofficial_covid19.config import Config

pdf_url = Config.PDF_URL
# 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて回避する
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
response = requests.get(pdf_url)
dfs = tabula.read_pdf(BytesIO(response.content), multiple_tables=True, lattice=True)
df = dfs[0]
df.columns = [
    "name1",
    "address1",
    "phone_number1",
    "book_at_medical_institution1",
    "book_at_call_center1",
    "name2",
    "address2",
    "phone_number2",
    "book_at_medical_institution2",
    "book_at_call_center2",
    "null",
]
# 見出し行を削除し、また、最終行が注釈なのでこれも削除
df.drop(df.index[[0, -1]], inplace=True)
# 最終列がNaNのみの列なので削除
df.drop(columns="null", inplace=True)
df.replace("\r", "", regex=True, inplace=True)
# 表が2段組なので左側の列のみを取り出す
left_df = df[
    [
        "name1",
        "address1",
        "phone_number1",
        "book_at_medical_institution1",
        "book_at_call_center1",
    ]
]
# 右側の列のみを取り出す
right_df = df[
    [
        "name2",
        "address2",
        "phone_number2",
        "book_at_medical_institution2",
        "book_at_call_center2",
    ]
]
left_df.columns = [
    "name",
    "address",
    "phone_number",
    "book_at_medical_institution",
    "book_at_call_center",
]
right_df.columns = [
    "name",
    "address",
    "phone_number",
    "book_at_medical_institution",
    "book_at_call_center",
]
formatted_df = pd.concat([left_df, right_df])
formatted_df.dropna(how="any", inplace=True)
formatted_df["address"] = formatted_df["address"].apply(lambda x: "旭川市" + x)
formatted_df["phone_number"] = formatted_df["phone_number"].apply(lambda x: "0166-" + x)
formatted_df["book_at_medical_institution"] = formatted_df[
    "book_at_medical_institution"
].apply(lambda x: x == "○")
formatted_df["book_at_call_center"] = formatted_df["book_at_call_center"].apply(
    lambda x: x == "○"
)

# TODO: 地域区分を取得する
formatted_df["area"] = ""
for row in formatted_df.to_dict(orient="records"):
    print(row)
