from ash_unofficial_covid19.models.area import Area, AreaFactory


class TestArea:
    def test_create(self):
        test_data = {"name": "西地区"}
        factory = AreaFactory()
        # Areaクラスのオブジェクトが生成できるか確認する。
        area = factory.create(**test_data)
        assert isinstance(area, Area)
        # 地区をURLパースした要素が生成されているか確認する。
        assert area.url == "%E8%A5%BF%E5%9C%B0%E5%8C%BA"
