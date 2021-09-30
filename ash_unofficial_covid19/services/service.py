import csv
from datetime import datetime
from io import StringIO

import psycopg2
from psycopg2.extras import DictCursor, execute_values

from ..config import Config
from ..errors import DatabaseConnectionError, ServiceError
from ..logs import AppLog


class Service:
    """新型コロナウイルス関連データを扱うサービスクラス"""

    def __init__(self, table_name: str):
        """
        Args:
            table_name (str): テーブル名

        """
        self.__table_name = table_name
        self.__dsn = Config.DATABASE_URL
        self.__logger = AppLog()

    @property
    def table_name(self):
        return self.__table_name

    def get_connection(self):
        """データベース接続オブジェクトを返す

        Returns:
            conn (:obj:`psycopg2.connection`): psycopg2.connectionオブジェクト

        """
        try:
            conn = psycopg2.connect(self.__dsn)
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            self.error_log("データベースに接続できませんでした。")
            raise DatabaseConnectionError(e.args[0])
        return conn

    def upsert(self, items: tuple, primary_key: str, data_lists: list) -> None:
        """データベースのテーブルへデータをバルクインサートでUPSERT登録する。

        Args:
            items (tuple): カラム名のタプル
            primary_key (str): UPSERTを判断するキー名
            data_lists (list of list): 登録データの二次元配列リスト

        """
        column_names = ""
        place_holders = ""
        upsert = ""
        for item in items:
            column_names += "," + item
            place_holders += ",%s"
            upsert += "," + item + "=EXCLUDED." + item

        state = (
            "INSERT INTO"
            + " "
            + self.table_name
            + " "
            + "("
            + column_names[1:]
            + ")"
            + " "
            + "VALUES %s"
            + " "
            + "ON CONFLICT("
            + primary_key
            + ")"
            + " "
            + "DO UPDATE SET"
            + " "
            + upsert[1:]
        )

        with self.get_connection() as conn:
            try:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    execute_values(cur, state, data_lists)
                conn.commit()
                data_number = len(data_lists)
                self.info_log(self.table_name + "テーブルへ" + str(data_number) + "件データを登録しました。")
            except (
                psycopg2.DataError,
                psycopg2.IntegrityError,
                psycopg2.InternalError,
            ) as e:
                self.error_log(self.table_name + "テーブルへデータを登録できませんでした。")
                raise ServiceError(e.args[0])

    def get_last_updated(self) -> datetime:
        """テーブルの最終更新日を返す

        Returns:
            last_updated (:obj:`datetime.datetime'): 最終更新日
                対象テーブルのupdatedカラムで一番最新の値を返す

        """
        state = "SELECT max(updated_at) FROM " + self.table_name + ";"
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                result = cur.fetchone()
        if result["max"] is None:
            return datetime(1970, 1, 1, 0, 0, 0)
        else:
            return result["max"]

    def info_log(self, message: str) -> None:
        """AppLogオブジェクトのinfoメソッドのラッパー

        Args:
            message (str): 通常のログメッセージ

        """
        if isinstance(message, str):
            self.__logger.info(message)
        else:
            self.__logger.info("通常メッセージの指定が正しくない")

    def error_log(self, message: str) -> None:
        """AppLogオブジェクトのerrorメソッドのラッパー

        Args:
            message (str): エラーログメッセージ

        """
        if isinstance(message, str):
            self.__logger.error(message)
        else:
            self.__logger.info("エラーメッセージの指定が正しくない")

    @staticmethod
    def get_csv(csv_rows) -> StringIO:
        """グラフのデータをCSVで返す

        Args:
            csv_rows (list of list): CSVにしたいデータを二次元配列で指定

        Returns:
            csv_data (StringIO): グラフのCSVデータ

        """
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(csv_rows)
        return f
