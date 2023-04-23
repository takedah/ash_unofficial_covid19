from ash_unofficial_covid19.models.reservation_status import (
    ReservationStatus,
    ReservationStatusFactory,
    ReservationStatusLocation,
    ReservationStatusLocationFactory,
)


class TestReservationStatus:
    def test_create(self):
        test_data = [
            {
                "area": "西地区",
                "medical_institution_name": "旭川赤十字病院",
                "division": "春開始接種（12歳以上）",
                "address": "曙1条1丁目",
                "phone_number": "76-9838(予約専用）",
                "vaccine": "モデルナ",
                "status": "受付中",
                "inoculation_time": "2/12～",
                "is_target_family": None,
                "is_target_not_family": False,
                "is_target_suberb": False,
                "memo": "当院ホームページをご確認ください",
            },
            {
                "area": "花咲町・末広・末広東・東鷹栖地区",
                "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
                "address": "花咲町7丁目",
                "phone_number": "51-3910予約専用",
                "division": "小児接種（３回目以降）",
                "vaccine": "ファイザー モデルナ",
                "status": "受付中",
                "inoculation_time": "2/1～",
                "is_target_family": True,
                "is_target_not_family": False,
                "is_target_suberb": None,
                "memo": "",
            },
            {
                "area": "西地区",
                "medical_institution_name": "旭川赤十字病院",
                "address": "曙1条1丁目",
                "phone_number": "76-9838(予約専用）",
                "division": "小児接種（３回目以降）",
                "vaccine": "モデルナ",
                "status": "受付中",
                "inoculation_time": "2/12～",
                "is_target_family": None,
                "is_target_not_family": False,
                "is_target_suberb": False,
                "memo": "かかりつけ患者以外は※条件あり 当院ホームページをご確認ください",
            },
        ]

        factory = ReservationStatusFactory()
        # ReservationStatusクラスのオブジェクトが生成できるか確認する。
        for d in test_data:
            reservation_status = factory.create(**d)
            assert isinstance(reservation_status, ReservationStatus)

    class TestReservationStatusLocation:
        def test_create(self):
            test_data = [
                {
                    "area": "西地区",
                    "medical_institution_name": "旭川赤十字病院",
                    "division": "春開始接種（12歳以上）",
                    "address": "曙1条1丁目",
                    "phone_number": "76-9838(予約専用）",
                    "vaccine": "モデルナ",
                    "status": "受付中",
                    "inoculation_time": "2/12～",
                    "is_target_family": None,
                    "is_target_not_family": False,
                    "is_target_suberb": False,
                    "longitude": 142.348303888889,
                    "latitude": 43.769628888889,
                    "memo": "当院ホームページをご確認ください",
                },
                {
                    "area": "花咲町・末広・末広東・東鷹栖地区",
                    "medical_institution_name": "独立行政法人国立病院機構旭川医療センター",
                    "address": "花咲町7丁目",
                    "phone_number": "51-3910予約専用",
                    "division": "小児接種（３回目以降）",
                    "vaccine": "ファイザー モデルナ",
                    "status": "受付中",
                    "inoculation_time": "2/1～",
                    "is_target_family": True,
                    "is_target_not_family": False,
                    "is_target_suberb": None,
                    "longitude": 142.3815237271935,
                    "latitude": 43.798826491523464,
                    "memo": "",
                },
                {
                    "area": "西地区",
                    "medical_institution_name": "旭川赤十字病院",
                    "address": "曙1条1丁目",
                    "phone_number": "76-9838(予約専用）",
                    "division": "小児接種（３回目以降）",
                    "vaccine": "モデルナ",
                    "status": "受付中",
                    "inoculation_time": "2/12～",
                    "is_target_family": None,
                    "is_target_not_family": False,
                    "is_target_suberb": False,
                    "longitude": 142.348303888889,
                    "latitude": 43.769628888889,
                    "memo": "かかりつけ患者以外は※条件あり 当院ホームページをご確認ください",
                },
            ]
            factory = ReservationStatusLocationFactory()
            # ReservationStatusLocationクラスのオブジェクトが生成できるか確認する。
            for d in test_data:
                reservation_status_location = factory.create(**d)
                assert isinstance(
                    reservation_status_location,
                    ReservationStatusLocation,
                )
            # 地区と医療機関名をURLパースした要素が生成されているか確認する。
            assert (
                reservation_status_location.division_url
                == "%E5%B0%8F%E5%85%90%E6%8E%A5%E7%A8%AE%EF%BC%88%EF%BC%93%E5%9B%9E%E7%9B%AE%E4%BB%A5%E9%99%8D%EF%BC%89"
            )
            assert reservation_status_location.area_url == "%E8%A5%BF%E5%9C%B0%E5%8C%BA"
            assert (
                reservation_status_location.medical_institution_name_url
                == "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2"
            )
