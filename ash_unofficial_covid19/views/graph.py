import re
from abc import abstractmethod
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO
from typing import Optional

from dateutil.relativedelta import relativedelta
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator
from PIL import Image

from ..services.patients_number import PatientsNumberService
from ..services.sapporo_patients_number import SapporoPatientsNumberService
from ..views.view import View


class GraphView(View):
    """グラフを出力するクラスの基底クラス"""

    @abstractmethod
    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        pass

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

    @staticmethod
    def _png_to_webp(png_data: BytesIO) -> BytesIO:
        """PNG形式のBytesIOをWebp形式に変換する。

        Args:
            png_data (BytesIO): PNG形式のBytesIOデータ

        Returns:
            webp_data (BytesIO): Webp形式のBytesIOデータ

        """
        image = Image.open(png_data)
        webp_data = BytesIO()
        image.save(webp_data, format="Webp")
        return webp_data


class DailyTotalView(GraphView):
    """日別累計患者数グラフ

    Attributes:
        today (str): 直近の日付
        most_recent (str): 直近の日別累積患者数
        seven_days_before_most_recent (str): 1週間前の日別累積患者数
        increase_from_seven_days_before (str): 1週間前の前日からの増加数
        graph_alt (str): グラフ画像の代替テキスト

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        service = PatientsNumberService()
        from_date = today - relativedelta(months=3)
        # 起算日が2020年2月23日の一週間より前の日付になってしまう場合は調整する。
        if from_date < date(2020, 2, 16):
            from_date = date(2020, 2, 16)
        self.__daily_total_data = service.get_aggregate_by_days(from_date=from_date, to_date=today)
        self.__today = self.format_date_style(today)
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
    def graph_alt(self):
        return self.__graph_alt

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        day_x = [row[0] for row in self.__daily_total_data]
        day_y = [row[1] for row in self.__daily_total_data]
        ax.bar(day_x, day_y, color="#4979F5")
        ax.yaxis.set_major_locator(MultipleLocator(50))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))
        ax.grid(axis="y", color="lightgray")
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        png_data = BytesIO()
        canvas.print_png(png_data)
        plt.cla()
        plt.clf()
        plt.close()
        return self._png_to_webp(png_data)


class MonthTotalView(GraphView):
    """月別累計患者数グラフ

    Attributes:
        today (str): 直近の日付
        this_month (str): 今月の月別累積患者数
        last_month (str): 前月の日別累積患者数
        increase_from_last_month (str): 前月からの増加数
        graph_alt (str): グラフ画像の代替テキスト

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        service = PatientsNumberService()
        self.__month_total_data = service.get_total_by_months(from_date=date(2020, 1, 1), to_date=today)
        self.__today = self.format_date_style(today)
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

    @property
    def graph_alt(self):
        return self.__graph_alt

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        # グラフの描画は直近12か月分のみとする
        month_total_data = self.__month_total_data[-12:]
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        month_total_x = [row[0].strftime("%Y-%m") for row in month_total_data]
        month_total_y = [row[1] for row in month_total_data]
        ax.bar(month_total_x, month_total_y, facecolor="#4979F5")
        ax.yaxis.set_major_locator(MultipleLocator(3000))
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        png_data = BytesIO()
        canvas.print_png(png_data)
        plt.cla()
        plt.clf()
        plt.close()
        return self._png_to_webp(png_data)


class ByAgeView(GraphView):
    """年代別患者数割合グラフ

    Attributes:
        graph_alt (str): グラフ画像の代替テキスト

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        service = PatientsNumberService()
        from_date = today - relativedelta(months=1, days=-1)
        # 起算日が2020年2月23日より前の日付になってしまう場合は調整する。
        if from_date < date(2020, 2, 23):
            from_date = date(2020, 2, 23)
        self.__by_age_data = service.get_patients_number_by_age(from_date=from_date, to_date=today)
        self.__graph_alt = ", ".join(["{0} {1}人".format(row[0], row[1]) for row in self.__by_age_data])

    @property
    def graph_alt(self):
        return self.__graph_alt

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansJP-Regular.otf",
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
            "#0946F1",
            "#4979F5",
            "#7096F8",
            "#9DB7F9",
            "#FF5838",
            "#FFA28B",
            "#FFE7E6",
            "#F1F1F4",
            "#D8D8DB",
            "#949497",
        ]
        ax.pie(
            by_age_x,
            labels=by_age_label,
            rotatelabels=True,
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
        png_data = BytesIO()
        canvas.print_png(png_data)
        plt.cla()
        plt.clf()
        plt.close()
        return self._png_to_webp(png_data)


class PerHundredThousandPopulationView(GraphView):
    """1週間の人口10万人あたり患者数グラフ

    Attributes:
        this_week (str): 今週の人口10万人あたり患者数
        last_week (str): 先週の人口10万人あたり患者数
        increase_from_last_week (str): 先週からの増加数
        graph_alt (str): グラフ画像の代替テキスト

    """

    def __init__(self, today: date):
        """
        Args:
            today (date): グラフを作成する基準日

        """
        service = PatientsNumberService()
        sapporo_service = SapporoPatientsNumberService()
        from_date = today - relativedelta(weeks=16, days=-1)
        # 起算日が2020年2月23日の二週間前より前の日付になってしまう場合は調整する。
        if from_date < date(2020, 2, 9):
            from_date = date(2020, 2, 9)
        sapporo_last_update_date = sapporo_service.get_last_update_date()
        self.__per_hundred_thousand_population_data = service.get_per_hundred_thousand_population_per_week(
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

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        font_file = "./ash_unofficial_covid19/static/fonts/NotoSansJP-Regular.otf"
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
            color="#4979F5",
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
            color="#949497",
            label="札幌市",
        )
        ax.yaxis.set_major_locator(MultipleLocator(50))
        ax.grid(axis="y", color="lightgray")
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        ax.legend(prop=legend_font, loc=0)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        png_data = BytesIO()
        canvas.print_png(png_data)
        plt.cla()
        plt.clf()
        plt.close()
        return self._png_to_webp(png_data)


class WeeklyPerAgeView(GraphView):
    """1週間ごとの年代別新規陽性患者数グラフ

    Attributes:
        graph_alt (str): グラフ画像の代替テキスト

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
        self.__aggregate_by_weeks_per_age = df
        self.__from_date = self.format_date_style(from_date)
        self.__graph_alt = self._get_graph_alt()

    @property
    def from_date(self):
        return self.__from_date

    @property
    def graph_alt(self):
        return self.__graph_alt

    def _get_graph_alt(self) -> str:
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
        font_file = "./ash_unofficial_covid19/static/fonts/NotoSansJP-Regular.otf"
        legend_font = FontProperties(fname=font_file, size=10)
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        colors = [
            "#0946F1",
            "#4979F5",
            "#7096F8",
            "#9DB7F9",
            "#FF5838",
            "#FFA28B",
            "#FFE7E6",
            "#F1F1F4",
            "#D8D8DB",
            "#949497",
            "#626264",
        ]
        cols = list(map(lambda x: x.strftime("%m-%d") + "~", df.columns.tolist()))
        for i in range(len(df)):
            ax.barh(
                cols,
                df.iloc[i],
                left=df.iloc[:i].sum(),
                color=colors[i],
            )

        min_x, max_x = ax.get_xlim()
        for rect in ax.patches:
            if 0.05 < rect.get_width() / max_x:
                cx = rect.get_x() + rect.get_width() / 2
                cy = rect.get_y() + rect.get_height() / 2
                label_value = f"{rect.get_width():.0f}"
                ax.text(cx, cy, label_value, ha="center", va="center", fontproperties=legend_font)

        ax.tick_params(labelsize=8)
        ax.legend(df.index.tolist(), prop=legend_font, loc=4)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        png_data = BytesIO()
        canvas.print_png(png_data)
        plt.cla()
        plt.clf()
        plt.close()
        return self._png_to_webp(png_data)
