from abc import abstractmethod
from datetime import date
from io import BytesIO
from typing import Optional

from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator
from PIL import Image

from ..services.database import ConnectionPool
from ..views.patients_number import (
    ByAgeView,
    DailyTotalView,
    MonthTotalView,
    PerHundredThousandPopulationView,
    WeeklyPerAgeView,
)
from ..views.view import View


class GraphView(View):
    """グラフを出力するクラスの基底クラス"""

    @abstractmethod
    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        pass

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


class DailyTotalGraphView(GraphView):
    """日別累計患者数グラフ"""

    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): グラフを作成する基準日
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        patients_numbers = DailyTotalView(today, pool)
        self._patients_numbers = patients_numbers

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
        day_x = [row[0] for row in self._patients_numbers.daily_total_data]
        day_y = [row[1] for row in self._patients_numbers.daily_total_data]
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


class MonthTotalGraphView(GraphView):
    """月別累計患者数グラフ"""

    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): グラフを作成する基準日
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        patients_numbers = MonthTotalView(today, pool)
        self._patients_numbers = patients_numbers

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        # グラフの描画は直近12か月分のみとする
        month_total_data = self._patients_numbers.month_total_data[-12:]
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


class ByAgeGraphView(GraphView):
    """年代別患者数割合グラフ"""

    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): グラフを作成する基準日
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        patients_numbers = ByAgeView(today, pool)
        self._patients_numbers = patients_numbers

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
        by_age_label = [row[0] for row in self._patients_numbers.by_age_data]
        by_age_x = [row[1] for row in self._patients_numbers.by_age_data]
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


class PerHundredThousandPopulationGraphView(GraphView):
    """1週間の人口10万人あたり患者数グラフ"""

    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): グラフを作成する基準日
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        patients_numbers = PerHundredThousandPopulationView(today, pool)
        self._patients_numbers = patients_numbers

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
            row[0].strftime("%m-%d") + "~" for row in self._patients_numbers.per_hundred_thousand_population_data
        ]
        per_hundred_thousand_population_y = [
            row[1] for row in self._patients_numbers.per_hundred_thousand_population_data
        ]
        ax.plot(
            per_hundred_thousand_population_x,
            per_hundred_thousand_population_y,
            color="#4979F5",
            label="旭川市",
        )
        sapporo_per_hundred_thousand_population_x = [
            row[0].strftime("%m-%d") + "~"
            for row in self._patients_numbers.sapporo_per_hundred_thousand_population_data
        ]
        sapporo_per_hundred_thousand_population_y = [
            row[1] for row in self._patients_numbers.sapporo_per_hundred_thousand_population_data
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


class WeeklyPerAgeGraphView(GraphView):
    """1週間ごとの年代別新規陽性患者数グラフ"""

    def __init__(self, today: date, pool: ConnectionPool):
        """
        Args:
            today (date): グラフを作成する基準日
            pool (:obj:`ConnectionPool`): SimpleConnectionPoolを要素に持つオブジェクト

        """
        patients_numbers = WeeklyPerAgeView(today, pool)
        self._patients_numbers = patients_numbers

    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        """グラフの画像を生成

        Args:
            figsize (tuple): グラフ画像データの縦横サイズを要素に持つタプル

        Returns:
            graph_image (BytesIO): グラフの画像データ

        """
        df = self._patients_numbers.weekly_per_age_data.transpose()
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
