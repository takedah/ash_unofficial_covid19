from datetime import date, datetime, timedelta, timezone

from psycopg2.extras import DictCursor

from ..models.press_release_link import PressReleaseLinkFactory
from ..services.service import Service


class PressReleaseLinkService(Service):
    """報道発表資料PDFファイル自体のデータを扱うサービス"""

    def __init__(self):
        Service.__init__(self, "press_release_links")

    def create(self, press_release_links: PressReleaseLinkFactory) -> None:
        """データベースへ報道発表資料PDFファイル自体のデータを保存

        Args:
            press_release_links (:obj:`PressReleaseLinkFactory`): PDFファイル自体のデータ
                報道発表資料PDFファイル自体のデータのオブジェクトのリストを要素に持つ
                オブジェクト

        """
        items = (
            "url",
            "publication_date",
            "updated_at",
        )

        data_lists = list()
        for press_release_link in press_release_links.items:
            data_lists.append(
                [
                    press_release_link.url,
                    press_release_link.publication_date,
                    datetime.now(timezone(timedelta(hours=+9))),
                ]
            )

        # データベースへ登録処理
        self.upsert(
            items=items,
            primary_key="publication_date",
            data_lists=data_lists,
        )

    def find_all(self) -> PressReleaseLinkFactory:
        """報道発表資料PDFファイル自体のデータの全件リストを返す

        Returns:
            res (:obj:`PressReleaseLinkFactory`): 報道発表資料PDFファイル自体のデータ一覧
                報道発表資料PDFファイル自体のデータのオブジェクトのリストを要素に持つ
                オブジェクト

        """
        state = (
            "SELECT"
            + " "
            + "url, publication_date"
            + " "
            + "FROM"
            + " "
            + self.table_name
            + " "
            + "ORDER BY publication_date DESC"
            + ";"
        )
        factory = PressReleaseLinkFactory()
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                for row in cur.fetchall():
                    factory.create(**row)
        return factory

    def get_latest_publication_date(self) -> date:
        """最新の報道発表日を返す

        Returns:
            publication_date (:obj:`datetime.date'): 最新の報道発表日

        """
        state = "SELECT max(publication_date) FROM " + self.table_name + ";"
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(state)
                result = cur.fetchone()

        latest_publication_date = result["max"]
        if isinstance(latest_publication_date, date):
            return latest_publication_date
        else:
            return date(1970, 1, 1)
