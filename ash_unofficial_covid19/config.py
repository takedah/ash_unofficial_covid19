import os


class Config:
    DATABASE_URL = os.environ.get("ASH_COVID19_DB_URL")
