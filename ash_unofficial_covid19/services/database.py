from urllib.parse import urlparse

import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.pool import SimpleConnectionPool

from ..config import Config
from ..errors import DatabaseConnectionError
from ..logs import AppLog


class ConnectionPool:
    """PostgreSQLサーバへの接続を管理する

    Attributes:
        pool (psycopg2.pool.SimpleConnectionPool): PostgreSQLへのコネクションプール

    """

    def __init__(self):
        logger = AppLog()
        url = urlparse(Config.DATABASE_URL)
        try:
            self.__pool = SimpleConnectionPool(
                minconn=2,
                maxconn=5,
                cursor_factory=DictCursor,
                database=url.path[1:],
                user=url.username,
                password=url.password,
                host=url.hostname,
                port=url.port,
            )
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            logger.error("データベースに接続できませんでした。")
            raise DatabaseConnectionError(e.args[0])

    def get_connection(self):
        return self.__pool.getconn()

    def return_connection(self, connection: DictCursor):
        """コネクションプールへ接続を返却する

        Args:
            connection (DictCursor): コネクションプールから生成したCursorオブジェクト

        """
        return self.__pool.putconn(connection)

    def close_connection(self):
        self.__pool.closeall()


class CursorFromConnectionPool:
    """
    コネクションプールからCursorオブジェクトを生成し、
    with句で処理が終わったら接続を返却できるようにする。

    """

    def __init__(self, pool: ConnectionPool):
        """
        Args:
            pool: SimpleConnectionPoolを要素に持つオブジェクト

        """
        self.__pool = pool
        self.__connection = None
        self.__cursor = None

    def __enter__(self):
        self.__connection = self.__pool.get_connection()
        self.__cursor = self.__connection.cursor()
        return self.__cursor

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_value is not None:
            self.__connection.rollback()
        else:
            self.__cursor.close()
            self.__connection.commit()

        self.__pool.return_connection(self.__connection)
