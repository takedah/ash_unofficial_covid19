import csv
from abc import ABCMeta
from io import StringIO


class View(metaclass=ABCMeta):
    """Viewに渡すデータを管理するクラスの基底クラス"""

    @staticmethod
    def list_to_csv(csv_rows) -> str:
        """グラフのデータをCSVで返す

        Args:
            csv_rows (list of list): CSVにしたいデータを二次元配列で指定

        Returns:
            csv_data (str): グラフのCSVデータ

        """
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(csv_rows)
        csv_data = f.getvalue()
        f.close()
        return csv_data
