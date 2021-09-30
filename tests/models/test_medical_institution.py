from ash_unofficial_covid19.models.medical_institution import MedicalInstitution, MedicalInstitutionFactory


def test_create():
    test_data = {
        "name": "市立旭川病院",
        "address": "金星町1",
        "phone_number": "0166-29-0202",
        "book_at_medical_institution": True,
        "book_at_call_center": False,
        "area": "",
        "memo": "",
        "target_age": "16歳以上",
    }
    factory = MedicalInstitutionFactory()
    # MedicalInstitutionクラスのオブジェクトが生成できるか確認する。
    medical_institution = factory.create(**test_data)
    assert isinstance(medical_institution, MedicalInstitution)
