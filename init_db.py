from ash_unofficial_covid19.errors import DatabaseConnectionError, ServiceError
from ash_unofficial_covid19.logs import AppLog
from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    HokkaidoPatientService,
    MedicalInstitutionService
)


def truncate_hokkaido_table() -> bool:
    """北海道の陽性患者属性データベースの初期化

    Returns:
        bool: データベースの初期化が成功したら真を返す

    """
    logger = AppLog()
    try:
        service = HokkaidoPatientService()
        service.delete_all()
    except (DatabaseConnectionError, ServiceError) as e:
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
        service = AsahikawaPatientService()
        service.delete_all()
    except (DatabaseConnectionError, ServiceError) as e:
        logger.warning(e.message)
        return False

    return True


def truncate_medical_institutions_table() -> bool:
    """旭川市新型コロナワクチン接種医療機関データベースの初期化

    Returns:
        bool: データベースの初期化が成功したら真を返す

    """
    logger = AppLog()
    try:
        service = MedicalInstitutionService()
        service.delete_all()
    except (DatabaseConnectionError, ServiceError) as e:
        logger.warning(e.message)
        return False

    return True


if __name__ == "__main__":
    truncate_hokkaido_table()
    truncate_asahikawa_table()
    truncate_medical_institutions_table()
