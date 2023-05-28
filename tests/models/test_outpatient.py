from ash_unofficial_covid19.models.outpatient import (
    Outpatient,
    OutpatientFactory,
    OutpatientLocation,
    OutpatientLocationFactory,
)


class TestOutpatient:
    def test_create(self):
        test_data = [
            {
                "is_outpatient": True,
                "is_positive_patients": True,
                "public_health_care_center": "旭川",
                "medical_institution_name": "市立旭川病院",
                "city": "旭川市",
                "address": "旭川市金星町1丁目1番65号",
                "phone_number": "0166-24-3181",
                "is_target_family": False,
                "is_pediatrics": True,
                "mon": "08:30～17:00",
                "tue": "08:30～17:00",
                "wed": "08:30～17:00",
                "thu": "08:30～17:00",
                "fri": "08:30～17:00",
                "sat": "",
                "sun": "",
                "is_face_to_face_for_positive_patients": True,
                "is_online_for_positive_patients": True,
                "is_home_visitation_for_positive_patients": False,
                "memo": "かかりつけ患者及び保健所からの紹介患者に限ります。 https://www.city.asahikawa.hokkaido.jp/hospital/3100/d075882.html",
            },
            {
                "is_outpatient": True,
                "is_positive_patients": False,
                "public_health_care_center": "旭川",
                "medical_institution_name": "JA北海道厚生連 旭川厚生病院",
                "city": "旭川市",
                "address": "旭川市1条通24丁目111番地",
                "phone_number": "0166-33-7171",
                "is_target_family": True,
                "is_pediatrics": False,
                "mon": "08:30～11:30",
                "tue": "08:30～11:30",
                "wed": "08:30～11:30",
                "thu": "08:30～11:30",
                "fri": "08:30～11:30",
                "sat": "",
                "sun": "",
                "is_face_to_face_for_positive_patients": False,
                "is_online_for_positive_patients": False,
                "is_home_visitation_for_positive_patients": False,
                "memo": "",
            },
            {
                "is_outpatient": True,
                "is_positive_patients": True,
                "public_health_care_center": "旭川",
                "medical_institution_name": "旭川赤十字病院",
                "city": "旭川市",
                "address": "旭川市曙1条1丁目1番1号",
                "phone_number": "0166-22-8111",
                "is_target_family": False,
                "is_pediatrics": False,
                "mon": "",
                "tue": "",
                "wed": "",
                "thu": "",
                "fri": "",
                "sat": "",
                "sun": "",
                "is_face_to_face_for_positive_patients": True,
                "is_online_for_positive_patients": False,
                "is_home_visitation_for_positive_patients": False,
                "memo": "「受診・相談センター」または保健所等の指示によら ず 受診した場合,初診時選定療養費を申し受けます。 当番制のため、不定期となっています。詳細はお問い合わせください。",
            },
        ]

        factory = OutpatientFactory()
        # Outpatientクラスのオブジェクトが生成できるか確認する。
        for d in test_data:
            outpatient = factory.create(**d)
            assert isinstance(outpatient, Outpatient)

    class TestOutpatientLocation:
        def test_create(self):
            test_data = [
                {
                    "is_outpatient": True,
                    "is_positive_patients": True,
                    "public_health_care_center": "旭川",
                    "medical_institution_name": "市立旭川病院",
                    "city": "旭川市",
                    "address": "旭川市金星町1丁目1番65号",
                    "phone_number": "0166-24-3181",
                    "is_target_family": False,
                    "is_pediatrics": True,
                    "mon": "08:30～17:00",
                    "tue": "08:30～17:00",
                    "wed": "08:30～17:00",
                    "thu": "08:30～17:00",
                    "fri": "08:30～17:00",
                    "sat": "",
                    "sun": "",
                    "is_face_to_face_for_positive_patients": True,
                    "is_online_for_positive_patients": True,
                    "is_home_visitation_for_positive_patients": False,
                    "memo": "かかりつけ患者及び保健所からの紹介患者に限ります。 "
                    + "https://www.city.asahikawa.hokkaido.jp/hospital/3100/d075882.html",
                    "longitude": 142.365952,
                    "latitude": 43.778144,
                },
                {
                    "is_outpatient": True,
                    "is_positive_patients": False,
                    "public_health_care_center": "旭川",
                    "medical_institution_name": "JA北海道厚生連 旭川厚生病院",
                    "city": "旭川市",
                    "address": "旭川市1条通24丁目111番地",
                    "phone_number": "0166-33-7171",
                    "is_target_family": True,
                    "is_pediatrics": False,
                    "mon": "08:30～11:30",
                    "tue": "08:30～11:30",
                    "wed": "08:30～11:30",
                    "thu": "08:30～11:30",
                    "fri": "08:30～11:30",
                    "sat": "",
                    "sun": "",
                    "is_face_to_face_for_positive_patients": False,
                    "is_online_for_positive_patients": False,
                    "is_home_visitation_for_positive_patients": False,
                    "memo": "",
                },
                {
                    "is_outpatient": True,
                    "is_positive_patients": True,
                    "public_health_care_center": "旭川",
                    "medical_institution_name": "旭川赤十字病院",
                    "city": "旭川市",
                    "address": "旭川市曙1条1丁目1番1号",
                    "phone_number": "0166-22-8111",
                    "is_target_family": False,
                    "is_pediatrics": False,
                    "mon": "",
                    "tue": "",
                    "wed": "",
                    "thu": "",
                    "fri": "",
                    "sat": "",
                    "sun": "",
                    "is_face_to_face_for_positive_patients": True,
                    "is_online_for_positive_patients": False,
                    "is_home_visitation_for_positive_patients": False,
                    "memo": "「受診・相談センター」または保健所等の指示によら ず 受診した場合,初診時選定療養費を申し受けます。 当番制のため、不定期となっています。詳細はお問い合わせください。",
                    "longitude": 142.348303888889,
                    "latitude": 43.769628888889,
                },
            ]
            factory = OutpatientLocationFactory()
            # OutpatientLocationクラスのオブジェクトが生成できるか確認する。
            for d in test_data:
                outpatient_location = factory.create(**d)
                assert isinstance(
                    outpatient_location,
                    OutpatientLocation,
                )
            # 医療機関名をURLパースした要素が生成されているか確認する。
            assert (
                outpatient_location.medical_institution_name_url
                == "%E6%97%AD%E5%B7%9D%E8%B5%A4%E5%8D%81%E5%AD%97%E7%97%85%E9%99%A2"
            )
