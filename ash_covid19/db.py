import psycopg2
from psycopg2.extras import DictCursor

from ash_covid19.config import Config
from ash_covid19.errors import DatabaseError


class DB:
    """PostgreSQLデータベースの操作を行う。

    Attributes:
        conn (:obj:`sqlite3.connect`): PostgreSQL接続クラス。

    """

    def __init__(self):
        try:
            self.__conn = psycopg2.connect(Config.DATABASE_URL)
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            raise DatabaseError(e.args[0])

    def cursor(self) -> DictCursor:
        """
        psycopg2.extras.DictCursorオブジェクトを返す。

        Returns:
            cursor (:obj:`DictCursor`): psycopg2.extras.DictCursorオブジェクト

        """
        return self.__conn.cursor(cursor_factory=DictCursor)

    def commit(self) -> None:
        """PostgreSQLデータベースにクエリをコミットする。"""
        self.__conn.commit()

    def rollback(self) -> None:
        """PostgreSQLデータベースのクエリをロールバックする。"""
        self.__conn.rollback()

    def close(self) -> None:
        """PostgreSQLデータベースへの接続を閉じる。"""
        self.__conn.close()
