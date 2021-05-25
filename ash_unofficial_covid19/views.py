import csv
import io
import os
from datetime import date, datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from io import BytesIO

from dateutil.relativedelta import relativedelta
from flask import Flask, g, make_response, render_template, url_for
from matplotlib import dates as mdates
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import MultipleLocator

from ash_unofficial_covid19.services import (
    AsahikawaPatientService,
    MedicalInstitutionService
)

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    response.headers.add(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' 'unsafe-inline' \
                stackpath.bootstrapcdn.com kit.fontawesome.com; \
                script-src 'self' code.jquery.com cdnjs.cloudflare.com \
                stackpath.bootstrapcdn.com kit.fontawesome.com; \
                connect-src ka-f.fontawesome.com; \
                font-src ka-f.fontawesome.com; \
                img-src 'self' i.creativecommons.org licensebuttons.net \
                data: https:;",
    )
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-Frame-Options", "DENY")
    response.headers.add("X-XSS-Protection", "1;mode=block")
    return response


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values["q"] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


def get_yesterday():
    return datetime.now(timezone(timedelta(hours=+9), "JST")).date() - relativedelta(
        days=1
    )


def get_day_data():
    # 日次新規陽性患者数データをグラフ描画処理でも使うためグローバル変数に格納しておく
    if not hasattr(g, "day_data"):
        yesterday = get_yesterday()
        patient_service = AsahikawaPatientService()
        g.day_data = patient_service.get_aggregate_by_days(
            from_date=yesterday - relativedelta(years=1), to_date=yesterday
        )
    return g.day_data


def get_moving_average_data():
    # 7日間移動平均データをグラフ描画処理でも使うためグローバル変数に格納しておく
    if not hasattr(g, "moving_average_data"):
        yesterday = get_yesterday()
        patient_service = AsahikawaPatientService()
        g.moving_average_data = patient_service.get_seven_days_moving_average(
            from_date=yesterday - relativedelta(months=3, days=1), to_date=yesterday
        )
    return g.moving_average_data


def get_month_total_data():
    # 月次累計陽性患者数データをグラフ描画処理でも使うためグローバル変数に格納しておく
    if not hasattr(g, "month_total_data"):
        yesterday = get_yesterday()
        patient_service = AsahikawaPatientService()
        g.month_total_data = patient_service.get_total_by_months(
            from_date=date(2020, 1, 1), to_date=yesterday
        )
    return g.month_total_data


def get_by_age_data():
    # 年代別患者数データをグラフ描画処理でも使うためグローバル変数に格納しておく
    if not hasattr(g, "by_age_data"):
        patient_service = AsahikawaPatientService()
        g.by_age_data = patient_service.get_patients_number_by_age()
    return g.by_age_data


@app.route("/")
def index():
    patient_service = AsahikawaPatientService()
    yesterday = get_yesterday()
    page_data = dict()

    # 日次集計
    day_data = get_day_data()
    page_data["day_graph_alt"] = ", ".join(
        ["{0}={1}".format(row[0].strftime("%m月%d日"), row[1]) for row in day_data]
    )
    yesterday_patients_number = day_data[-1][1]
    day_before_yesterday_patients_number = day_data[-2][1]
    increase_of_day_before_yesterday = (
        yesterday_patients_number - day_before_yesterday_patients_number
    )
    page_data["yesterday_patients_number"] = "{:,}".format(yesterday_patients_number)
    page_data["day_before_yesterday_patients_number"] = "{:,}".format(
        day_before_yesterday_patients_number
    )
    page_data["increase_of_day_before_yesterday"] = "{:+,}".format(
        increase_of_day_before_yesterday
    )

    # 7日間移動平均集計
    moving_average_data = get_moving_average_data()
    page_data["moving_average_graph_alt"] = ", ".join(
        [
            "{0}={1}".format(row[0].strftime("%m月%d日"), row[1])
            for row in moving_average_data
        ]
    )
    this_seven_days_average = moving_average_data[-1][1]
    last_seven_days_average = moving_average_data[-2][1]
    increase_of_average = float(
        Decimal(str(this_seven_days_average - last_seven_days_average)).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    )
    page_data["this_seven_days_average"] = "{:,}".format(this_seven_days_average)
    page_data["last_seven_days_average"] = "{:,}".format(last_seven_days_average)
    page_data["increase_of_average"] = "{:+,}".format(increase_of_average)

    # 月次集計
    month_total_data = get_month_total_data()
    page_data["month_total_graph_alt"] = ", ".join(
        [
            "{0}={1}".format(row[0].strftime("%Y年%m月"), row[1])
            for row in month_total_data
        ]
    )
    total_patients_number = month_total_data[-1][1]
    last_month_total_patients_number = month_total_data[-2][1]
    increase_of_total = total_patients_number - last_month_total_patients_number
    page_data["total_patients_number"] = "{:,}".format(total_patients_number)
    page_data["last_month_total_patients_number"] = "{:,}".format(
        last_month_total_patients_number
    )
    page_data["increase_of_total"] = "{:+,}".format(increase_of_total)

    # 年代別集計
    by_age_data = get_by_age_data()
    page_data["by_age_graph_alt"] = ", ".join(
        ["{0}={1}".format(row[0], row[1]) for row in by_age_data]
    )

    title = "旭川市新型コロナウイルスまとめサイト"
    last_updated = patient_service.get_last_updated()
    return render_template(
        "index.html",
        title=title,
        last_updated=last_updated.strftime("%Y/%m/%d %H:%M"),
        yesterday=yesterday.strftime("%Y/%m/%d (%a)"),
        page_data=page_data,
    )


@app.route("/about")
def about():
    title = "旭川市新型コロナウイルスまとめサイトについて"
    return render_template(
        "about.html",
        title=title,
    )


@app.route("/opendata")
def opendata():
    patient_service = AsahikawaPatientService()
    last_updated = patient_service.get_last_updated()
    title = "旭川市新型コロナウイルス非公式オープンデータ（陽性者属性CSV）"
    return render_template(
        "opendata.html",
        title=title,
        last_updated=last_updated.strftime("%Y/%m/%d %H:%M"),
    )


@app.route("/medical_institutions")
def medical_institutions():
    medical_institution_service = MedicalInstitutionService()
    medical_institutions_rows = medical_institution_service.get_csv_rows()
    medical_institutions_rows.pop(0)
    title = "旭川市新型コロナワクチン接種医療機関一覧"
    last_updated = medical_institution_service.get_last_updated()
    return render_template(
        "medical_institutions.html",
        title=title,
        last_updated=last_updated.strftime("%Y/%m/%d %H:%M"),
        medical_institutions=medical_institutions_rows,
    )


@app.route("/012041_asahikawa_covid19_patients.csv")
def patients_csv():
    patient_service = AsahikawaPatientService()
    patients_rows = patient_service.get_csv_rows()
    f = io.StringIO()
    writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerows(patients_rows)
    res = make_response()
    res.data = f.getvalue()
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "012041_asahikawa_covid19_patients.csv"
    )
    return res


@app.route("/012041_asahikawa_covid19_medical_institutions.csv")
def medical_institutions_csv():
    medical_institution_service = MedicalInstitutionService()
    medical_institutions_rows = medical_institution_service.get_csv_rows()
    f = io.StringIO()
    writer = csv.writer(f, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerows(medical_institutions_rows)
    res = make_response()
    res.data = f.getvalue()
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "012041_asahikawa_covid19_medical_institutions.csv"
    )
    return res


@app.route("/day_per_patients.png")
def get_day_graph():
    day_data = get_day_data()
    font = FontProperties(
        fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf", size=12
    )
    fig = plt.figure()
    ax = fig.add_subplot()
    day_x = [row[0] for row in day_data]
    day_y = [row[1] for row in day_data]
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
    graph_image = im.getvalue()
    res = make_response()
    res.data = graph_image
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "day_per_patients.png"
    )
    return res


@app.route("/seven_days_moving_average.png")
def get_moving_average_graph():
    moving_average_data = get_moving_average_data()
    font = FontProperties(
        fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf", size=12
    )
    fig = plt.figure()
    ax = fig.add_subplot()
    moving_average_x = [row[0].strftime("%m-%d") + "~" for row in moving_average_data]
    moving_average_y = [row[1] for row in moving_average_data]
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
    graph_image = im.getvalue()
    res = make_response()
    res.data = graph_image
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "seven_days_moving_average.png"
    )
    return res


@app.route("/month_total_patients.png")
def get_month_total_graph():
    month_total_data = get_month_total_data()
    # グラフの描画は直近12か月分のみとする
    month_total_data = month_total_data[-12:]
    font = FontProperties(
        fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf", size=12
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
    graph_image = im.getvalue()
    res = make_response()
    res.data = graph_image
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "month_total_patients.png"
    )
    return res


@app.route("/patients_number_by_age.png")
def get_by_age_graph():
    by_age_data = get_by_age_data()
    font = FontProperties(
        fname="./ash_unofficial_covid19/static/fonts/NotoSansCJKjp-Light.otf", size=12
    )
    fig = plt.figure()
    ax = fig.add_subplot()
    by_age_label = [row[0] for row in by_age_data]
    by_age_x = [row[1] for row in by_age_data]
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
    graph_image = im.getvalue()
    res = make_response()
    res.data = graph_image
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "patients_number_by_age.png"
    )
    return res


@app.errorhandler(404)
def not_found(error):
    title = "404 Page Not Found."
    return render_template("404.html", title=title)


if __name__ == "__main__":
    app.run()
