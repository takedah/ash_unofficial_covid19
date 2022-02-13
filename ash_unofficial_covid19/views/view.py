import csv
import json
from abc import ABCMeta
from io import StringIO


class View(metaclass=ABCMeta):
    """Viewに渡すデータを管理するクラスの基底クラス"""

    @staticmethod
    def list_to_csv(rows) -> str:
        """二次元配列のデータをCSVで返す

        Args:
            rows (list of list): CSVにしたいデータを二次元配列で指定

        Returns:
            csv_data (str): CSV文字列データ

        """
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(rows)
        csv_data = f.getvalue()
        f.close()
        return csv_data

    @staticmethod
    def dict_to_json(rows) -> str:
        """辞書のデータをJSONで返す

        Args:
            rows (list of list): JSONにしたいデータを辞書で指定

        Returns:
            json_data (str): JSON文字列データ

        """
        json_bytes = json.dumps(rows).encode()
        return json_bytes.decode("unicode-escape")
