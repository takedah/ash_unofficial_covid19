import unicodedata
from datetime import date
from typing import Union

import camelot

from ..scrapers.scraper import Scraper


class ScrapePatientsNumber(Scraper):
    """旭川市新型コロナウイルス陽性患者数データの抽出

    旭川市公式ホームページからダウンロードしたPDFファイルのデータから、
    旭川市の新型コロナウイルス新規陽性患者数データを抽出し、リストに変換する。

    Attributes:
        asahikawa_patients_data (list of dict): 旭川市の新規陽性患者数データ
            旭川市の新型コロナウイルス新規陽性患者データを表す辞書のリスト

    """

    def __init__(self, pdf_url: str, publication_date: date):
        """
        Args:
            pdf_url (str): PDFファイルのURL
                旭川市の報道発表PDFファイルのURL
           publication_date (date): 報道発表日
                報道発表PDFデータに公表日がないため、引数で指定した日付をセット

        """
        Scraper.__init__(self)
        pdf_df = self._get_dataframes(pdf_url)
        if isinstance(publication_date, date):
            self.__lists = self._get_patients_number(pdf_df, publication_date)
        else:
            raise TypeError("報道発表日の指定が正しくありません。")

    @property
    def lists(self) -> list:
        return self.__lists

    def _get_dataframes(self, pdf_url: str) -> list:
        """
        Args:
            pdf_url (str): PDFファイルのURL
                旭川市の報道発表PDFファイルのURL

        Returns:
            dataframes (list of obj:`pd.DataFrame`): 旭川市の新型コロナ報道発表PDFデータ
                旭川市の新型コロナウイルス報道発表PDFデータから抽出した表データを、
                pandas DataFrameのリストで返す。

        """
        tables = camelot.read_pdf(pdf_url)
        dataframes = list()
        for table in tables:
            dataframes.append(table.df)
        return dataframes

    def _get_patients_number(self, pdf_df: list, publication_date: date) -> list:
        """
        Args:
            pdf_df (list of :obj:`pd.DataFrame`): PDFファイルから抽出した表データ
            publication_date (date): 報道発表日

        Returns:
            patients_number_data (dict): 新型コロナウイルス陽性患者数PDFデータ
                旭川市の新型コロナウイルス陽性患者報道発表PDFデータから抽出した
                年代別陽性患者数データを辞書で返す。

        """
        patients_number_data = list()
        for df in pdf_df:
            # データフレームが空の場合スキップ
            if df.empty:
                continue

            df.dropna(how="all", inplace=True)
            df.drop_duplicates(inplace=True)
            df.fillna("", inplace=True)
            pdf_table = df.values.tolist()
            # リスト化した結果空リストだった場合スキップ
            if pdf_table == []:
                continue

            patients_number: dict[str, Union[date, int]] = dict()
            patients_number["publication_date"] = publication_date

            if publication_date > date(2022, 9, 26):
                for row in pdf_table:
                    if row is None:
                        continue

                    if self._nomalize(row[0].split("\n")[0]) == "全体":
                        age_under_10 = (
                            int(self._nomalize(row[1].split("\n")[0]))
                            + int(self._nomalize(row[2].split("\n")[0]))
                            + int(self._nomalize(row[3].split("\n")[0]))
                        )
                        age_60s = int(self._nomalize(row[9].split("\n")[0])) + int(
                            self._nomalize(row[10].split("\n")[0])
                        )
                        patients_number["age_under_10"] = age_under_10
                        patients_number["age_10s"] = int(self._nomalize(row[4].split("\n")[0]))
                        patients_number["age_20s"] = int(self._nomalize(row[5].split("\n")[0]))
                        patients_number["age_30s"] = int(self._nomalize(row[6].split("\n")[0]))
                        patients_number["age_40s"] = int(self._nomalize(row[7].split("\n")[0]))
                        patients_number["age_50s"] = int(self._nomalize(row[8].split("\n")[0]))
                        patients_number["age_60s"] = age_60s
                        patients_number["age_70s"] = int(self._nomalize(row[10].split("\n")[1]))
                        patients_number["age_80s"] = int(self._nomalize(row[10].split("\n")[2]))
                        patients_number["age_over_90"] = int(self._nomalize(row[10].split("\n")[3]))
                        patients_number["investigating"] = 0
                        patients_number_data.append(patients_number)
                        return patients_number_data

            else:
                # 年齢別陽性患者数内訳以外の表だった場合スキップ
                label_column = self._nomalize(pdf_table[0][0])
                if label_column != "10歳未満":
                    continue

                for row in pdf_table:
                    age = self._nomalize(str(row[0]))
                    try:
                        number = int(self._nomalize(str(row[1])))
                    except ValueError:
                        number = 0

                    if age == "10歳未満":
                        patients_number["age_under_10"] = number
                    elif age == "10歳代":
                        patients_number["age_10s"] = number
                    elif age == "20歳代":
                        patients_number["age_20s"] = number
                    elif age == "30歳代":
                        patients_number["age_30s"] = number
                    elif age == "40歳代":
                        patients_number["age_40s"] = number
                    elif age == "50歳代":
                        patients_number["age_50s"] = number
                    elif age == "60歳代":
                        patients_number["age_60s"] = number
                    elif age == "70歳代":
                        patients_number["age_70s"] = number
                    elif age == "80歳代":
                        patients_number["age_80s"] = number
                    elif age == "90歳以上":
                        patients_number["age_over_90"] = number
                    else:
                        patients_number["investigating"] = number

                patients_number_data.append(patients_number)
                return patients_number_data

        # PDFに年代別内訳表がない場合、その報道発表日の患者数は全年代0とする
        if len(patients_number_data) == 0:
            patients_number_data.append({"publication_date": publication_date})

        return patients_number_data

    @staticmethod
    def _nomalize(text: str) -> str:
        """文字列から余計な空白等を取り除き、全角数字等を正規化して返す。

        Args:
            text (str): 正規化したい文字列

        Returns:
            nomalized_text (str): 正規化後の文字列

        """
        if not isinstance(text, str):
            return ""

        return unicodedata.normalize("NFKC", text.strip().replace(" ", "").replace("　", ""))
