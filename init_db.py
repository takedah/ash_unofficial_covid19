from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.errors import (
    DatabaseError,
    DataError,
    DataModelError
)
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    HokkaidoPatientService
)


def truncate_hokkaido_table() -> bool:
    """北海道の陽性患者属性データベースの初期化

    Returns:
        bool: データベースの初期化が成功したら真を返す

    """
    logger = AppLog()
    try:
        conn = DB()
        service = HokkaidoPatientService(conn)
        service.truncate()
        conn.commit()
        conn.close()
    except (DataError, DatabaseError, DataModelError) as e:
        conn.close()
        logger.warning(e.message)
        return False

    return True


def truncate_asahikawa_table() -> bool:
    """旭川市の陽性患者属性データベースの初期化

    Returns:
        bool: データベースの初期化が成功したら真を返す

    """
    logger = AppLog()
    try:
        conn = DB()
        service = AsahikawaPatientService(conn)
        service.truncate()
        conn.commit()
        conn.close()
    except (DataError, DatabaseError, DataModelError) as e:
        conn.close()
        logger.warning(e.message)
        return False

    return True


if __name__ == "__main__":
    truncate_hokkaido_table()
    truncate_asahikawa_table()
