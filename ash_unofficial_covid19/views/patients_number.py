import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta

from ..services.patients_number import PatientsNumberService
from ..services.sapporo_patients_number import SapporoPatientsNumberService
from ..views.view import View


class PatientsNumberView(View):
    """旭川市新型コロナウイルス感染症陽性患者数データ

    旭川市新型コロナウイルス感染症陽性患者数データをFlaskへ渡すデータにする

    Attributes:
        today (date): データを作成する基準日
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): データを作成する基準日

        """
        self._service = PatientsNumberService()
        self._today = today
        last_updated = self._service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self):
        return self.__last_updated

    @staticmethod
    def format_date_style(target_date: date) -> str:
        """datetime.dateを曜日を含めた文字列に変換

        Args:
            target_date (date): 対象の日付

        Returns:
            date_string (str): 曜日を含む日付文字列

        """
        if isinstance(target_date, date):
            target_date_to_string = target_date.strftime("%Y/%m/%d %a")
        else:
            return ""

        search_strings = re.match(
            "^([0-9]{4}/[0-9]{2}/[0-9]{2}) ([A-Z][a-z]{2})$",
            target_date_to_string,
        )

        if search_strings is None:
            return ""
        else:
            date_string = search_strings.group(1)
            day_of_week = search_strings.group(2)

        if day_of_week == "Mon":
            day_of_week_kanji = "月"
        elif day_of_week == "Tue":
            day_of_week_kanji = "火"
        elif day_of_week == "Wed":
            day_of_week_kanji = "水"
        elif day_of_week == "Thu":
            day_of_week_kanji = "木"
        elif day_of_week == "Fri":
            day_of_week_kanji = "金"
        elif day_of_week == "Sat":
            day_of_week_kanji = "土"
        elif day_of_week == "Sun":
            day_of_week_kanji = "日"
        else:
            day_of_week_kanji = ""

        return date_string + " (" + day_of_week_kanji + ") "

    def get_daily_total_csv(self) -> str:
        """陽性患者日計CSVファイルの文字列データを返す

        Returns:
            csv_data (str): 陽性患者日計CSVファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        csv_data = self._service.get_aggregate_by_days(from_date=from_date, to_date=self._today)
        csv_data.insert(
            0,
            [
                "公表日",
                "陽性患者数",
            ],
        )
        return self.list_to_csv(csv_data)

    def get_daily_total_json(self) -> str:
        """陽性患者日計JSONファイルの文字列データを返す

        Returns:
            json_data (str): 陽性患者日計JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        aggregate_by_days = self._service.get_aggregate_by_days(from_date=from_date, to_date=self._today)
        json_data = dict((d.strftime("%Y-%m-%d"), n) for d, n in aggregate_by_days)
        return self.dict_to_json(json_data)

    def get_daily_total_per_age_csv(self) -> str:
        """陽性患者年代別日計CSVファイルの文字列データを返す

        Returns:
            json_data (str): 日別年代別陽性患者数JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        csv_data = self._service.get_lists(from_date=from_date, to_date=self._today)
        csv_data.insert(
            0,
            ["公表日", "10歳未満", "10代", "20代", "30代", "40代", "50代", "60代", "70代", "80代", "90歳以上", "調査中等"],
        )
        return self.list_to_csv(csv_data)

    def get_daily_total_per_age_json(self) -> str:
        """陽性患者年代別日計JSONファイルの文字列データを返す

        Returns:
            json_data (str): 日別年代別陽性患者数JSONファイルの文字列データ

        """
        from_date = date(2020, 2, 23)
        json_data = self._service.get_dicts(from_date=from_date, to_date=self._today)
        return self.dict_to_json(json_data)


class DailyTotalView(PatientsNumberView):
    """日別累計患者数グラフ

    Attributes:
        reference_date (str): 直近の日付
        most_recent (str): 直近の日別累積患者数
        seven_days_before_most_recent (str): 1週間前の日別累積患者数
        increase_from_seven_days_before (str): 1週間前の前日からの増加数
        graph_alt (str): グラフ画像の代替テキスト
        daily_total_data (list): グラフ用に集計したデータ

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        PatientsNumberView.__init__(self, today)
        from_date = today - relativedelta(months=3)
        # 起算日が2020年2月23日の一週間より前の日付になってしまう場合は調整する。
        if from_date < date(2020, 2, 16):
            from_date = date(2020, 2, 16)
        self.__daily_total_data = self._service.get_aggregate_by_days(from_date=from_date, to_date=today)
        self.__reference_date = self.format_date_style(today)
        most_recent = self.__daily_total_data[-1][1]
        seven_days_before_most_recent = self.__daily_total_data[-8][1]
        increase_from_seven_days_before = most_recent - seven_days_before_most_recent
        self.__most_recent = "{:,}".format(most_recent)
        self.__seven_days_before_most_recent = "{:,}".format(seven_days_before_most_recent)
        self.__increase_from_seven_days_before = "{:+,}".format(increase_from_seven_days_before)
        self.__graph_alt = ", ".join(
            ["{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1]) for row in self.__daily_total_data[-7:]]
        )

    @property
    def reference_date(self):
        return self.__reference_date

    @property
    def most_recent(self):
        return self.__most_recent

    @property
    def seven_days_before_most_recent(self):
        return self.__seven_days_before_most_recent

    @property
    def increase_from_seven_days_before(self):
        return self.__increase_from_seven_days_before

    @property
    def graph_alt(self):
        return self.__graph_alt

    @property
    def daily_total_data(self):
        return self.__daily_total_data


class MonthTotalView(PatientsNumberView):
    """月別累計患者数グラフ

    Attributes:
        reference_date (str): 直近の日付
        this_month (str): 今月の月別累積患者数
        last_month (str): 前月の日別累積患者数
        increase_from_last_month (str): 前月からの増加数
        graph_alt (str): グラフ画像の代替テキスト
        month_total_data (list): グラフ用に集計したデータ

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        PatientsNumberView.__init__(self, today)
        self.__month_total_data = self._service.get_total_by_months(from_date=date(2020, 1, 1), to_date=today)
        self.__reference_date = self.format_date_style(today)
        this_month = self.__month_total_data[-1][1]
        last_month = self.__month_total_data[-2][1]
        increase_from_last_month = this_month - last_month
        self.__this_month = "{:,}".format(this_month)
        self.__last_month = "{:,}".format(last_month)
        self.__increase_from_last_month = "{:+,}".format(increase_from_last_month)
        self.__graph_alt = ", ".join(
            ["{0} {1}人".format(row[0].strftime("%Y年%m月"), row[1]) for row in self.__month_total_data[-6:]]
        )

    @property
    def reference_date(self):
        return self.__reference_date

    @property
    def this_month(self):
        return self.__this_month

    @property
    def last_month(self):
        return self.__last_month

    @property
    def increase_from_last_month(self):
        return self.__increase_from_last_month

    @property
    def graph_alt(self):
        return self.__graph_alt

    @property
    def month_total_data(self):
        return self.__month_total_data


class ByAgeView(PatientsNumberView):
    """年代別患者数割合グラフ

    Attributes:
        graph_alt (str): グラフ画像の代替テキスト
        by_age_data (list): グラフ用に集計したデータ

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        PatientsNumberView.__init__(self, today)
        from_date = today - relativedelta(months=1, days=-1)
        # 起算日が2020年2月23日より前の日付になってしまう場合は調整する。
        if from_date < date(2020, 2, 23):
            from_date = date(2020, 2, 23)
        self.__by_age_data = self._service.get_patients_number_by_age(from_date=from_date, to_date=today)
        self.__graph_alt = ", ".join(["{0} {1}人".format(row[0], row[1]) for row in self.__by_age_data])

    @property
    def graph_alt(self):
        return self.__graph_alt

    @property
    def by_age_data(self):
        return self.__by_age_data


class PerHundredThousandPopulationView(PatientsNumberView):
    """1週間の人口10万人あたり患者数グラフ

    Attributes:
        this_week (str): 今週の人口10万人あたり患者数
        last_week (str): 先週の人口10万人あたり患者数
        increase_from_last_week (str): 先週からの増加数
        graph_alt (str): グラフ画像の代替テキスト
        per_hundred_thousand_population_data (list): グラフ用に集計したデータ
        sapporo_per_hundred_thousand_population_data (list): グラフ用に集計した札幌市のデータ

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        PatientsNumberView.__init__(self, today)
        sapporo_service = SapporoPatientsNumberService()
        from_date = today - relativedelta(weeks=16, days=-1)
        # 起算日が2020年2月23日の二週間前より前の日付になってしまう場合は調整する。
        if from_date < date(2020, 2, 9):
            from_date = date(2020, 2, 9)
        sapporo_last_update_date = sapporo_service.get_last_update_date()
        self.__per_hundred_thousand_population_data = self._service.get_per_hundred_thousand_population_per_week(
            from_date=from_date,
            to_date=today,
        )
        sapporo_per_hundred_thousand_population_data = sapporo_service.get_per_hundred_thousand_population_per_week(
            from_date=from_date,
            to_date=sapporo_last_update_date,
        )
        if sapporo_last_update_date < today:
            del sapporo_per_hundred_thousand_population_data[-1:]

        self.__sapporo_per_hundred_thousand_population_data = sapporo_per_hundred_thousand_population_data
        this_week = self.__per_hundred_thousand_population_data[-1][1]
        last_week = self.__per_hundred_thousand_population_data[-2][1]
        increase_from_last_week = float(
            Decimal(str(this_week - last_week)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        self.__this_week = "{:,}".format(this_week)
        self.__last_week = "{:,}".format(last_week)
        self.__increase_from_last_week = "{:+,}".format(increase_from_last_week)
        self.__graph_alt = ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1])
                for row in self.__per_hundred_thousand_population_data
            ]
        )

    @property
    def this_week(self):
        return self.__this_week

    @property
    def last_week(self):
        return self.__last_week

    @property
    def increase_from_last_week(self):
        return self.__increase_from_last_week

    @property
    def graph_alt(self):
        return self.__graph_alt

    @property
    def per_hundred_thousand_population_data(self):
        return self.__per_hundred_thousand_population_data

    @property
    def sapporo_per_hundred_thousand_population_data(self):
        return self.__sapporo_per_hundred_thousand_population_data


class WeeklyPerAgeView(PatientsNumberView):
    """1週間ごとの年代別新規陽性患者数グラフ

    Attributes:
        graph_alt (str): グラフ画像の代替テキスト
        weekly_per_age_data (list): グラフ用に集計したデータ

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        service = PatientsNumberService()
        from_date = today - relativedelta(weeks=4, days=-1)
        # 起算日が2020年2月23日より前の日付になってしまう場合は調整する。
        if from_date < date(2020, 2, 23):
            from_date = date(2020, 2, 23)
        df = service.get_aggregate_by_weeks_per_age(from_date=from_date, to_date=today)
        self.__weekly_per_age_data = df
        self.__from_date = self.format_date_style(from_date)
        self.__graph_alt = self._get_graph_alt()

    @property
    def from_date(self):
        return self.__from_date

    @property
    def graph_alt(self):
        return self.__graph_alt

    @property
    def weekly_per_age_data(self):
        return self.__weekly_per_age_data

    def _get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        alt_text = ""
        cols = self.weekly_per_age_data.columns.tolist()
        for index, row in self.weekly_per_age_data.iterrows():
            i = 0
            alt_text = alt_text + index.strftime("%m月%d日以降") + " "
            for value in row:
                alt_text = alt_text + cols[i] + ": " + str(value) + "人,"
                i += 1
        return alt_text
