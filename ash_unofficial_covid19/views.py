import csv
from abc import ABCMeta, abstractclassmethod
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO, StringIO

from dateutil.relativedelta import relativedelta
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator

from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    MedicalInstitutionService
)


class AsahikawaPatientsView:
    def __init__(self):
        self.__service = AsahikawaPatientService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self) -> str:
        return self.__last_updated

    def get_csv(self) -> StringIO:
        rows = self.__service.get_csv_rows()
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(rows)
        return f


class MedicalInstitutionsView:
    def __init__(self):
        self.__service = MedicalInstitutionService()
        last_updated = self.__service.get_last_updated()
        self.__last_updated = last_updated.strftime("%Y/%m/%d %H:%M")

    @property
    def last_updated(self) -> str:
        return self.__last_updated

    def get_rows(self) -> list:
        csv_rows = self.__service.get_csv_rows()
        csv_rows.pop(0)
        return csv_rows

    def get_csv(self) -> StringIO:
        csv_rows = self.__service.get_csv_rows()
        f = StringIO()
        writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
        writer.writerows(csv_rows)
        return f


class GraphView(metaclass=ABCMeta):
    @abstractclassmethod
    def get_graph_alt(self) -> str:
        pass

    @abstractclassmethod
    def get_graph_image(self) -> BytesIO:
        pass

    def get_yesterday(self) -> date:
        now = datetime.now(timezone(timedelta(hours=+9), "JST"))
        today = now.date()
        # 市の発表が15時が多いので、15時より前なら前々日の情報を表示するようにする
        if now.hour < 15:
            adjust_days = 2
        else:
            adjust_days = 1
        return today - relativedelta(days=adjust_days)


class DailyTotalView(GraphView):
    def __init__(self):
        service = AsahikawaPatientService()
        yesterday = self.get_yesterday()
        self.__daily_total_data = service.get_aggregate_by_days(
            from_date=yesterday - relativedelta(years=1), to_date=yesterday
        )
        self.__yesterday = yesterday.strftime("%Y/%m/%d (%a)")
        most_recent = self.__daily_total_data[-1][1]
        day_before_most_recent = self.__daily_total_data[-2][1]
        increase_from_day_before = most_recent - day_before_most_recent
        self.__most_recent = "{:,}".format(most_recent)
        self.__day_before_most_recent = "{:,}".format(day_before_most_recent)
        self.__increase_from_day_before = "{:+,}".format(increase_from_day_before)

    @property
    def yesterday(self) -> str:
        return self.__yesterday

    @property
    def most_recent(self) -> str:
        return self.__most_recent

    @property
    def day_before_most_recent(self) -> str:
        return self.__day_before_most_recent

    @property
    def increase_from_day_before(self) -> str:
        return self.__increase_from_day_before

    def get_graph_alt(self) -> str:
        return ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1])
                for row in self.__daily_total_data[-14:]
            ]
        )

    def get_graph_image(self) -> BytesIO:
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
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
        return ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月"), row[1])
                for row in self.__month_total_data
            ]
        )

    def get_graph_image(self) -> BytesIO:
        # グラフの描画は直近12か月分のみとする
        month_total_data = self.__month_total_data[-12:]
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
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
    def __init__(self):
        service = AsahikawaPatientService()
        self.__by_age_data = service.get_patients_number_by_age()

    def get_graph_alt(self) -> str:
        return ", ".join(
            ["{0} {1}人".format(row[0], row[1]) for row in self.__by_age_data]
        )

    def get_graph_image(self):
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
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
        return ", ".join(
            [
                "{0} {1}人".format(row[0].strftime("%Y年%m月%d日"), row[1])
                for row in self.__moving_average_data
            ]
        )

    def get_graph_image(self) -> BytesIO:
        font = FontProperties(
            fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf",
            size=12,
        )
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
