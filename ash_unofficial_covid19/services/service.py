from abc import ABCMeta
from datetime import datetime

import psycopg2
from psycopg2.extras import execute_values

from ..errors import ServiceError
from ..logs import AppLog
from ..services.database import ConnectionPool, CursorFromConnectionPool


class Service(metaclass=ABCMeta):
    """新型コロナウイルス関連データを扱うサービスクラス"""

    def __init__(self, table_name: str, pool: ConnectionPool):
        """
        Args:
            table_name (str): テーブル名
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        self.__table_name = table_name
        self.__pool = pool
        self.__logger = AppLog()

    @property
    def table_name(self):
        return self.__table_name

    def get_connection(self):
        """データベース接続オブジェクトを返す

        Args:

        Returns:
            conn (:obj:`CursorFromConnectionPool`): with句でDictCursorを返すオブジェクト

        """
        return CursorFromConnectionPool(self.__pool)

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

        try:
            with self.get_connection() as cur:
                execute_values(cur, state, data_lists)

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
        with self.get_connection() as cur:
            cur.execute(state)
            result = cur.fetchone()

        if result["max"] is None:
            return datetime(1970, 1, 1, 0, 0, 0)

        last_updated = result["max"]
        if isinstance(last_updated, datetime):
            return last_updated
        else:
            return datetime(1970, 1, 1, 0, 0, 0)

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
