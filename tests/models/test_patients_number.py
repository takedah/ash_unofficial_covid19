from datetime import date

import pytest

from ash_unofficial_covid19.models.patients_number import PatientsNumber, PatientsNumberFactory


class TestPatientsNumber:
    def test_create(self):
        test_data = {
            "publication_date": date(2022, 1, 28),
            "age_under_10": 12,
            "age_10s": 19,
            "age_20s": 12,
            "age_30s": 14,
            "age_40s": 13,
            "age_50s": 15,
            "age_60s": 3,
            "age_70s": 2,
            "age_80s": 2,
            "age_over_90": 0,
            "investigating": 5,
        }
        factory = PatientsNumberFactory()
        patients_number = factory.create(**test_data)
        assert isinstance(patients_number, PatientsNumber)

    def test_create_with_incomplete_args(self):
        # 年代の指定がない場合デフォルト値がセットされる
        test_data = {
            "publication_date": date(2022, 1, 28),
            "age_under_10": 12,
            "age_10s": 19,
            "age_30s": 14,
            "age_40s": 13,
            "age_50s": 15,
            "age_60s": 3,
            "age_70s": 2,
            "age_80s": 2,
            "age_over_90": 0,
            "investigating": 5,
        }
        factory = PatientsNumberFactory()
        patients_number = factory.create(**test_data)
        assert patients_number.age_20s == 0

    def test_create_with_invalid_args(self):
        # 報道発表日が指定されていない場合エラーを返す
        test_data = {
            "age_under_10": 12,
            "age_10s": 19,
            "age_20s": 12,
            "age_30s": 14,
            "age_40s": 13,
            "age_50s": 15,
            "age_60s": 3,
            "age_70s": 2,
            "age_80s": 2,
            "age_over_90": 0,
            "investigating": 5,
        }
        factory = PatientsNumberFactory()
        with pytest.raises(TypeError):
            factory.create(**test_data)
