import re
from abc import ABCMeta, abstractmethod
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO
from typing import Optional

from dateutil.relativedelta import relativedelta
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator

from ..errors import DatabaseConnectionError
from ..services.patient import AsahikawaPatientService
from ..services.press_release_link import PressReleaseLinkService
from ..services.sapporo_patients_number import SapporoPatientsNumberService


class GraphView(metaclass=ABCMeta):
    """グラフを出力するクラスの基底クラス"""

    @abstractmethod
    def get_graph_alt(self) -> str:
        pass

    @abstractmethod
    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        pass

    @staticmethod
    def get_today() -> date:
        """グラフの基準となる最新の報道発表日の日付を返す

        Returns:
            today (date): 最新の報道発表日の日付データ

        """
        now = datetime.now(timezone(timedelta(hours=+9), "JST"))
        try:
            press_release_link_service = PressReleaseLinkService()
            today = press_release_link_service.get_latest_publication_date()
        except DatabaseConnectionError:
            # エラーが起きた場合現在日付を基準とする。
            # このとき市の発表が16時になることが多いので16時より前なら前日を基準とする。
            today = now.date()
            if now.hour < 16:
                today = today - relativedelta(days=1)

        return today

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


class DailyTotalView(GraphView):
    """日別累計患者数グラフ

    Attributes:
        today (str): 直近の日付
        most_recent (str): 直近の日別累積患者数
        day_before_most_recent (str): 直近の前日の日別累積患者数
        increase_from_day_before (str): 直近の前日からの増加数
        reproduction_number (str): 実行再生産数の簡易推定値

    """

    def __init__(self):
        service = AsahikawaPatientService()
        today = self.get_today()
        self.__daily_total_data = service.get_aggregate_by_days(
            from_date=today - relativedelta(years=1), to_date=today
        )
        self.__today = self.format_date_style(today)
        most_recent = self.__daily_total_data[-1][1]
        seven_days_before_most_recent = self.__daily_total_data[-8][1]
        increase_from_seven_days_before = most_recent - seven_days_before_most_recent
        self.__most_recent = "{:,}".format(most_recent)
        self.__seven_days_before_most_recent = "{:,}".format(seven_days_before_most_recent)
        self.__increase_from_seven_days_before = "{:+,}".format(increase_from_seven_days_before)
        reproduction_number = service.get_reproduction_number(today)
        if reproduction_number < 1:
            self.__reproduction_status = "1を下回っており感染減少傾向にある"
        else:
            self.__reproduction_status = "1以上であり感染拡大傾向にある"
        self.__reproduction_number = str(reproduction_number)

    @property
    def today(self):
        return self.__today

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
    def reproduction_number(self):
        return self.__reproduction_number

    @property
    def reproduction_status(self):
        return self.__reproduction_status

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(
            ["{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1]) for row in self.__daily_total_data[-14:]]
        )

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        day_x = [row[0] for row in self.__daily_total_data]
        day_y = [row[1] for row in self.__daily_total_data]
        ax.bar(day_x, day_y, color="salmon")
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax.grid(axis="y", color="lightgray")
        ax.set_title("旭川市新規感染者数の推移（日次）", font_properties=font)
        ax.set_ylabel("新規感染者数（人）", font_properties=font)
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        im = BytesIO()
        canvas.print_png(im)
        plt.cla()
        plt.clf()
        plt.close()
        return im


class MonthTotalView(GraphView):
    """月別累計患者数グラフ

    Attributes:
        today (str): 直近の日付
        this_month (str): 今月の月別累積患者数
        last_month (str): 前月の日別累積患者数
        increase_from_last_month (str): 前月からの増加数

    """

    def __init__(self):
        service = AsahikawaPatientService()
        today = self.get_today()
        self.__month_total_data = service.get_total_by_months(from_date=date(2020, 1, 1), to_date=today)
        self.__today = self.format_date_style(today)
        this_month = self.__month_total_data[-1][1]
        last_month = self.__month_total_data[-2][1]
        increase_from_last_month = this_month - last_month
        self.__this_month = "{:,}".format(this_month)
        self.__last_month = "{:,}".format(last_month)
        self.__increase_from_last_month = "{:+,}".format(increase_from_last_month)

    @property
    def today(self):
        return self.__today

    @property
    def this_month(self):
        return self.__this_month

    @property
    def last_month(self):
        return self.__last_month

    @property
    def increase_from_last_month(self):
        return self.__increase_from_last_month

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(["{0} {1}人".format(row[0].strftime("%Y年%m月"), row[1]) for row in self.__month_total_data])

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        # グラフの描画は直近12か月分のみとする
        month_total_data = self.__month_total_data[-12:]
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        month_total_x = [row[0].strftime("%Y-%m") for row in month_total_data]
        month_total_y = [row[1] for row in month_total_data]
        ax.bar(month_total_x, month_total_y, facecolor="salmon")
        ax.yaxis.set_major_locator(MultipleLocator(100))
        ax.grid(axis="y", color="lightgray")
        ax.set_title("旭川市累計感染者数の推移（月次）", font_properties=font)
        ax.set_ylabel("累計感染者数（人）", font_properties=font)
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        im = BytesIO()
        canvas.print_png(im)
        plt.cla()
        plt.clf()
        plt.close()
        return im


class ByAgeView(GraphView):
    """年代別患者数割合グラフ"""

    def __init__(self):
        service = AsahikawaPatientService()
        today = self.get_today()
        self.__by_age_data = service.get_patients_number_by_age(
            from_date=today - relativedelta(months=1, days=-1), to_date=today
        )
        self.__today = self.format_date_style(today)

    @property
    def today(self):
        return self.__today

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(["{0} {1}人".format(row[0], row[1]) for row in self.__by_age_data])

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        by_age_label = [row[0] for row in self.__by_age_data]
        by_age_x = [row[1] for row in self.__by_age_data]
        pie_colors = [
            "mistyrose",
            "peachpuff",
            "lightsalmon",
            "salmon",
            "coral",
            "lemonchiffon",
            "palegoldenrod",
            "khaki",
            "darkkhaki",
            "goldenrod",
        ]
        ax.pie(
            by_age_x,
            labels=by_age_label,
            autopct=lambda p: "{:.1f}%".format(p) if p >= 3 else "",
            startangle=90,
            radius=1.3,
            labeldistance=1.1,
            pctdistance=0.7,
            colors=pie_colors,
            counterclock=False,
            textprops={"font_properties": font},
        )
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        im = BytesIO()
        canvas.print_png(im)
        plt.cla()
        plt.clf()
        plt.close()
        return im


class MovingAverageView(GraphView):
    """1日あたり患者数の7日間移動平均グラフ

    Attributes:
        today (str): 直近の日付
        this_week (str): 今週の平均患者数
        last_week (str): 先週の平均患者数
        increase_from_last_week (str): 先週からの増加数

    """

    def __init__(self):
        service = AsahikawaPatientService()
        today = self.get_today()
        self.__moving_average_data = service.get_seven_days_moving_average(
            from_date=today - relativedelta(days=90), to_date=today
        )
        this_week = self.__moving_average_data[-1][1]
        last_week = self.__moving_average_data[-2][1]
        increase_from_last_week = float(
            Decimal(str(this_week - last_week)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        self.__this_week = "{:,}".format(this_week)
        self.__last_week = "{:,}".format(last_week)
        self.__increase_from_last_week = "{:+,}".format(increase_from_last_week)

    @property
    def this_week(self):
        return self.__this_week

    @property
    def last_week(self):
        return self.__last_week

    @property
    def increase_from_last_week(self):
        return self.__increase_from_last_week

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(
            ["{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1]) for row in self.__moving_average_data]
        )

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        moving_average_x = [row[0].strftime("%m-%d") + "~" for row in self.__moving_average_data]
        moving_average_y = [row[1] for row in self.__moving_average_data]
        ax.plot(moving_average_x, moving_average_y, color="salmon")
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.grid(axis="y", color="lightgray")
        ax.set_title("旭川市新規感染者数の7日間移動平均の推移", font_properties=font)
        ax.set_ylabel("7日間移動平均（人/1日あたり）", font_properties=font)
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        im = BytesIO()
        canvas.print_png(im)
        plt.cla()
        plt.clf()
        plt.close()
        return im


class PerHundredThousandPopulationView(GraphView):
    """1週間の人口10万人あたり患者数グラフ

    Attributes:
        today (str): 直近の日付
        this_week (str): 今週の人口10万人あたり患者数
        last_week (str): 先週の人口10万人あたり患者数
        increase_from_last_week (str): 先週からの増加数
        alert_level (str): 警戒レベル
            1週間の人口10万人あたり患者数を基準とした北海道の警戒レベル

    """

    def __init__(self):
        service = AsahikawaPatientService()
        sapporo_service = SapporoPatientsNumberService()
        today = self.get_today()
        self.__per_hundred_thousand_population_data = service.get_per_hundred_thousand_population_per_week(
            from_date=today - relativedelta(weeks=16, days=-1),
            to_date=today,
        )
        self.__sapporo_per_hundred_thousand_population_data = (
            sapporo_service.get_per_hundred_thousand_population_per_week(
                from_date=today - relativedelta(weeks=16, days=-1),
                to_date=today,
            )
        )
        this_week = self.__per_hundred_thousand_population_data[-1][1]
        last_week = self.__per_hundred_thousand_population_data[-2][1]
        increase_from_last_week = float(
            Decimal(str(this_week - last_week)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        )
        alert_level = self._get_alert_level(this_week)
        self.__this_week = "{:,}".format(this_week)
        self.__last_week = "{:,}".format(last_week)
        self.__increase_from_last_week = "{:+,}".format(increase_from_last_week)
        self.__alert_level = alert_level

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
    def alert_level(self):
        return self.__alert_level

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1])
                for row in self.__per_hundred_thousand_population_data
            ]
        )

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        font_file = "./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf"
        font = FontProperties(fname=font_file, size=12)
        legend_font = FontProperties(fname=font_file, size=10)
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        per_hundred_thousand_population_x = [
            row[0].strftime("%m-%d") + "~" for row in self.__per_hundred_thousand_population_data
        ]
        per_hundred_thousand_population_y = [row[1] for row in self.__per_hundred_thousand_population_data]
        ax.plot(
            per_hundred_thousand_population_x,
            per_hundred_thousand_population_y,
            color="salmon",
            label="旭川市",
        )
        sapporo_per_hundred_thousand_population_x = [
            row[0].strftime("%m-%d") + "~" for row in self.__sapporo_per_hundred_thousand_population_data
        ]
        sapporo_per_hundred_thousand_population_y = [
            row[1] for row in self.__sapporo_per_hundred_thousand_population_data
        ]
        ax.plot(
            sapporo_per_hundred_thousand_population_x,
            sapporo_per_hundred_thousand_population_y,
            color="lightgray",
            label="札幌市",
        )
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.grid(axis="y", color="lightgray")
        ax.set_title("旭川市1週間の人口10万人あたり新規感染者数の推移", font_properties=font)
        ax.set_ylabel("1週間の新規感染者数（人/人口10万人あたり）", font_properties=font)
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        ax.legend(prop=legend_font, loc=0)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        im = BytesIO()
        canvas.print_png(im)
        plt.cla()
        plt.clf()
        plt.close()
        return im

    @staticmethod
    def _get_alert_level(per_hundred_thousand_population: float) -> str:
        """北海道の警戒ステージレベルを返す

        Args:
            per_hundred_thousand_population (float): 1週間の人口10万人あたり新規陽性患者数

        Returns:
            alert_level (str): 北海道の警戒ステージレベル

        """
        if per_hundred_thousand_population >= 15:
            return "警戒を強化すべきレベル"
        else:
            return ""


class WeeklyPerAgeView(GraphView):
    """1週間ごとの年代別新規陽性患者数グラフ"""

    def __init__(self):
        service = AsahikawaPatientService()
        today = self.get_today()
        from_date = today - relativedelta(weeks=4, days=-1)
        df = service.get_aggregate_by_weeks_per_age(from_date=from_date, to_date=today)
        self.__aggregate_by_weeks_per_age = df
        self.__today = self.format_date_style(today)
        self.__from_date = self.format_date_style(from_date)

    @property
    def today(self):
        return self.__today

    @property
    def from_date(self):
        return self.__from_date

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        df = self.__aggregate_by_weeks_per_age
        alt_text = ""
        cols = df.columns.tolist()
        for index, row in df.iterrows():
            i = 0
            alt_text = alt_text + index.strftime("%m月%d日以降") + " "
            for value in row:
                alt_text = alt_text + cols[i] + ": " + str(value) + "人,"
                i += 1
        return alt_text

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        df = self.__aggregate_by_weeks_per_age.transpose()
        font_file = "./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf"
        font = FontProperties(fname=font_file, size=12)
        legend_font = FontProperties(fname=font_file, size=10)
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        colors = [
            "mistyrose",
            "peachpuff",
            "lightsalmon",
            "salmon",
            "coral",
            "lemonchiffon",
            "palegoldenrod",
            "khaki",
            "darkkhaki",
            "goldenrod",
            "floralwhite",
        ]
        cols = list(map(lambda x: x.strftime("%m-%d") + "~", df.columns.tolist()))
        for i in range(len(df)):
            ax.barh(
                cols,
                df.iloc[i],
                left=df.iloc[:i].sum(),
                color=colors[i],
            )
        ax.tick_params(labelsize=8)
        ax.set_title("旭川市年代別新規感染者数の推移（週別）", font_properties=font)
        ax.legend(df.index.tolist(), prop=legend_font, loc=4)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        im = BytesIO()
        canvas.print_png(im)
        plt.cla()
        plt.clf()
        plt.close()
        return im
