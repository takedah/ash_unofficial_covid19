import csv
import re
import urllib.parse
from abc import ABCMeta, abstractmethod
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO, StringIO
from typing import Optional

from dateutil.relativedelta import relativedelta
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator

from ash_unofficial_covid19.errors import DatabaseConnectionError
from ash_unofficial_covid19.services.medical_institution import (
    MedicalInstitutionService
)
from ash_unofficial_covid19.services.patient import AsahikawaPatientService
from ash_unofficial_covid19.services.press_release_link import (
    PressReleaseLinkService
)


class AsahikawaPatientsView:
    """旭川市新型コロナウイルス陽性患者データ

    旭川市新型コロナウイルス陽性患者データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = AsahikawaPatientService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self) -> str:
        return self.__last_updated

    def get_csv(self) -> StringIO:
        """グラフのデータをCSVで返す

        Returns:
            csv_data (StringIO): グラフのCSVデータ

        """
        csv_rows = self.__service.get_csv_rows()
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(csv_rows)
        return f

    def get_rows(self, page: int = 1, desc: bool = True) -> tuple:
        """グラフのデータをオブジェクトデータのリストで返す

        ページネーションできるよう指定したページ番号分のデータのみ返す

        Args:
            page (int): ページ番号
            desc (bool): 真なら降順、偽なら昇順でリストを返す

        Returns:
            rows (tuple): ページネーションデータ
                AsahikawaPatientFactoryオブジェクトと
                ページネーションした場合の最大ページ数の数値を要素に持つタプル

        """
        return self.__service.find(page=page, desc=desc)


class MedicalInstitutionsView:
    """旭川市新型コロナワクチン接種医療機関データ

    旭川市新型コロナワクチン接種医療機関データをFlaskへ渡すデータにする

    Attributes:
        last_updated (str): 最終更新日の文字列

    """

    def __init__(self):
        self.__service = MedicalInstitutionService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self) -> str:
        return self.__last_updated

    def get_locations(self, area: Optional[str] = None) -> list:
        """位置情報付きで新型コロナワクチン接種医療機関一覧のデータを返す

        Args:
            area (str): 医療機関の地区

        Returns:
            locations (list of tuple): 位置情報付きの接種医療機関データリスト
                新型コロナワクチン接種医療機関の情報に緯度経度を含めたタプルのリスト

        """
        return self.__service.get_locations(area=area)

    def get_area_list(self) -> list:
        """新型コロナワクチン接種医療機関の地域全件のリストを返す

        Returns:
            res (list of tuple): 医療機関の地域一覧リスト
                医療機関の地域名称とそれをURLエンコードした文字列と対で返す

        """
        area_list = list()
        for area in self.__service.get_area_list():
            area_list.append((area, urllib.parse.quote(area)))
        return area_list

    def get_csv(self) -> StringIO:
        """新型コロナワクチン接種医療機関一覧のデータをCSVで返す

        Returns:
            csv_data (StringIO): 新型コロナワクチン接種医療機関一覧のCSVデータ

        """
        csv_rows = self.__service.get_csv_rows()
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(csv_rows)
        return f


class PressReleaseLinksView:
    """旭川市新型コロナ報道発表資料データ

    旭川市新型コロナの報道発表資料データをFlaskへ渡すデータにする

    Attributes:
        latest_publication_date (str): 最新の報道発表日の文字列

    """

    def __init__(self):
        self.__service = PressReleaseLinkService()
        latest_publication_date = self.__service.get_latest_publication_date()
        self.__latest_publication_date = self._format_date_style(
            latest_publication_date
        )

    @property
    def latest_publication_date(self) -> str:
        return self.__latest_publication_date

    def _format_date_style(self, target_date: date) -> str:
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


class GraphView(metaclass=ABCMeta):
    """グラフを出力するクラスの基底クラス"""

    @abstractmethod
    def get_graph_alt(self) -> str:
        pass

    @abstractmethod
    def get_graph_image(self, figsize: Optional[tuple] = None) -> BytesIO:
        pass

    def get_yesterday(self) -> date:
        """グラフの基準となる最新の報道発表日の前日の日付を返す

        Returns:
            yesterday (date): 前日の日付データ

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

        return today - relativedelta(days=1)


class DailyTotalView(GraphView):
    """日別累計患者数グラフ

    Attributes:
        yesterday (str): 直近の日付
        most_recent (str): 直近の日別累積患者数
        day_before_most_recent (str): 直近の前日の日別累積患者数
        increase_from_day_before (str): 直近の前日からの増加数

    """

    def __init__(self):
        service = AsahikawaPatientService()
        yesterday = self.get_yesterday()
        self.__daily_total_data = service.get_aggregate_by_days(
            from_date=yesterday - relativedelta(years=1), to_date=yesterday
        )
        self.__yesterday = yesterday.strftime("%Y/%m/%d (%a)")
        most_recent = self.__daily_total_data[-1][1]
        seven_days_before_most_recent = self.__daily_total_data[-8][1]
        increase_from_seven_days_before = most_recent - seven_days_before_most_recent
        self.__most_recent = "{:,}".format(most_recent)
        self.__seven_days_before_most_recent = "{:,}".format(
            seven_days_before_most_recent
        )
        self.__increase_from_seven_days_before = "{:+,}".format(
            increase_from_seven_days_before
        )

    @property
    def yesterday(self) -> str:
        return self.__yesterday

    @property
    def most_recent(self) -> str:
        return self.__most_recent

    @property
    def seven_days_before_most_recent(self) -> str:
        return self.__seven_days_before_most_recent

    @property
    def increase_from_seven_days_before(self) -> str:
        return self.__increase_from_seven_days_before

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1])
                for row in self.__daily_total_data[-14:]
            ]
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
        ax.set_title("旭川市新規陽性患者数の推移（日次）", font_properties=font)
        ax.set_ylabel("新規陽性患者数（人）", font_properties=font)
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
        yesterday (str): 直近の日付
        this_month (str): 今月の月別累積患者数
        last_month (str): 前月の日別累積患者数
        increase_from_last_month (str): 前月からの増加数

    """

    def __init__(self):
        service = AsahikawaPatientService()
        yesterday = self.get_yesterday()
        self.__month_total_data = service.get_total_by_months(
            from_date=date(2020, 1, 1), to_date=yesterday
        )
        self.__yesterday = yesterday.strftime("%Y/%m/%d (%a)")
        this_month = self.__month_total_data[-1][1]
        last_month = self.__month_total_data[-2][1]
        increase_from_last_month = this_month - last_month
        self.__this_month = "{:,}".format(this_month)
        self.__last_month = "{:,}".format(last_month)
        self.__increase_from_last_month = "{:+,}".format(increase_from_last_month)

    @property
    def yesterday(self) -> str:
        return self.__yesterday

    @property
    def this_month(self) -> str:
        return self.__this_month

    @property
    def last_month(self) -> str:
        return self.__last_month

    @property
    def increase_from_last_month(self) -> str:
        return self.__increase_from_last_month

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月"), row[1])
                for row in self.__month_total_data
            ]
        )

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
        ax.set_title("旭川市累計陽性患者数の推移（月次）", font_properties=font)
        ax.set_ylabel("累計陽性患者数（人）", font_properties=font)
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
    """年代別患者数グラフ"""

    def __init__(self):
        service = AsahikawaPatientService()
        self.__by_age_data = service.get_patients_number_by_age()

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(
            ["{0} {1}人".format(row[0], row[1]) for row in self.__by_age_data]
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
        by_age_label = [row[0] for row in self.__by_age_data]
        by_age_x = [row[1] for row in self.__by_age_data]
        pie_colors = [
            "orange",
            "oldlace",
            "wheat",
            "moccasin",
            "papayawhip",
            "blanchedalmond",
            "navajowhite",
            "tan",
            "antiquewhite",
            "burlywood",
        ]
        ax.pie(
            by_age_x,
            labels=by_age_label,
            autopct="%1.1f %%",
            startangle=90,
            radius=1.3,
            labeldistance=1.1,
            pctdistance=0.7,
            colors=pie_colors,
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
        yesterday (str): 直近の日付
        this_week (str): 今週の平均患者数
        last_week (str): 先週の平均患者数
        increase_from_last_week (str): 先週からの増加数

    """

    def __init__(self):
        service = AsahikawaPatientService()
        yesterday = self.get_yesterday()
        self.__moving_average_data = service.get_seven_days_moving_average(
            from_date=yesterday - relativedelta(days=90), to_date=yesterday
        )
        this_week = self.__moving_average_data[-1][1]
        last_week = self.__moving_average_data[-2][1]
        increase_from_last_week = float(
            Decimal(str(this_week - last_week)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )
        self.__this_week = "{:,}".format(this_week)
        self.__last_week = "{:,}".format(last_week)
        self.__increase_from_last_week = "{:+,}".format(increase_from_last_week)

    @property
    def this_week(self) -> str:
        return self.__this_week

    @property
    def last_week(self) -> str:
        return self.__last_week

    @property
    def increase_from_last_week(self) -> str:
        return self.__increase_from_last_week

    def get_graph_alt(self) -> str:
        """グラフの代替テキストを生成

        Returns:
            graph_alt (str): グラフの代替テキスト

        """
        return ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1])
                for row in self.__moving_average_data
            ]
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
        moving_average_x = [
            row[0].strftime("%m-%d") + "~" for row in self.__moving_average_data
        ]
        moving_average_y = [row[1] for row in self.__moving_average_data]
        ax.plot(moving_average_x, moving_average_y, color="salmon")
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.grid(axis="y", color="lightgray")
        ax.set_title("旭川市新規陽性患者数の7日間移動平均の推移", font_properties=font)
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
        yesterday (str): 直近の日付
        this_week (str): 今週の人口10万人あたり患者数
        last_week (str): 先週の人口10万人あたり患者数
        increase_from_last_week (str): 先週からの増加数
        alert_level (str): 警戒レベル
            1週間の人口10万人あたり患者数を基準とした北海道の警戒レベル

    """

    def __init__(self):
        service = AsahikawaPatientService()
        yesterday = self.get_yesterday()
        self.__per_hundred_thousand_population_data = (
            service.get_per_hundred_thousand_population_per_week(
                from_date=yesterday - relativedelta(weeks=16, days=-1),
                to_date=yesterday,
            )
        )
        this_week = self.__per_hundred_thousand_population_data[-1][1]
        last_week = self.__per_hundred_thousand_population_data[-2][1]
        increase_from_last_week = float(
            Decimal(str(this_week - last_week)).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        )
        alert_level = self._get_alert_level(this_week)
        self.__this_week = "{:,}".format(this_week)
        self.__last_week = "{:,}".format(last_week)
        self.__increase_from_last_week = "{:+,}".format(increase_from_last_week)
        self.__alert_level = alert_level

    @property
    def this_week(self) -> str:
        return self.__this_week

    @property
    def last_week(self) -> str:
        return self.__last_week

    @property
    def increase_from_last_week(self) -> str:
        return self.__increase_from_last_week

    @property
    def alert_level(self) -> str:
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
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
        if figsize:
            fig = plt.figure(figsize=figsize)
        else:
            fig = plt.figure()
        ax = fig.add_subplot()
        per_hundred_thousand_population_x = [
            row[0].strftime("%m-%d") + "~"
            for row in self.__per_hundred_thousand_population_data
        ]
        per_hundred_thousand_population_y = [
            row[1] for row in self.__per_hundred_thousand_population_data
        ]
        ax.plot(
            per_hundred_thousand_population_x,
            per_hundred_thousand_population_y,
            color="salmon",
        )
        ax.yaxis.set_major_locator(MultipleLocator(5))
        ax.grid(axis="y", color="lightgray")
        ax.set_title("旭川市1週間の人口10万人あたり新規陽性患者数の推移", font_properties=font)
        ax.set_ylabel("1週間の新規陽性患者数（人/人口10万人あたり）", font_properties=font)
        ax.tick_params(labelsize=8)
        ax.tick_params(axis="x", rotation=45)
        ax.text(
            per_hundred_thousand_population_x[0],
            15,
            "警戒ステージ3",
            va="center",
            ha="left",
            backgroundcolor="white",
            font_properties=font,
        )
        ax.axhline(y=15, color="orange", linewidth=1, linestyle="--")
        ax.text(
            per_hundred_thousand_population_x[0],
            25,
            "警戒ステージ4",
            va="center",
            ha="left",
            backgroundcolor="white",
            font_properties=font,
        )
        ax.axhline(y=25, color="salmon", linewidth=1, linestyle="--")
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
        if per_hundred_thousand_population >= 25:
            return "警戒ステージ4相当（緊急事態宣言の目安）"
        elif per_hundred_thousand_population >= 15:
            return "警戒ステージ3相当（まん延防止等重点措置の目安）"
        elif per_hundred_thousand_population >= 2.0:
            return "警戒ステージ2相当"
        else:
            return "警戒ステージ1相当"


class WeeklyPerAgeView(GraphView):
    """1週間ごとの年代別新規陽性患者数グラフ"""

    def __init__(self):
        service = AsahikawaPatientService()
        yesterday = self.get_yesterday()
        df = service.get_aggregate_by_weeks_per_age(
            from_date=yesterday - relativedelta(weeks=4, days=-1), to_date=yesterday
        )
        self.__aggregate_by_weeks_per_age = df

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
            "lightblue",
            "gold",
            "yellowgreen",
            "tomato",
            "plum",
            "peru",
            "lightpink",
            "cornflowerblue",
            "tan",
            "paleturquoise",
            "whitesmoke",
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
        ax.set_title("旭川市年代別新規陽性患者数の推移（週別）", font_properties=font)
        ax.legend(df.index.tolist(), prop=legend_font)
        fig.tight_layout()
        canvas = FigureCanvasAgg(fig)
        im = BytesIO()
        canvas.print_png(im)
        plt.cla()
        plt.clf()
        plt.close()
        return im
