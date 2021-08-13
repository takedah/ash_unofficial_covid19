import os

from flask import (
    Flask,
    abort,
    escape,
    g,
    make_response,
    render_template,
    url_for
)

from ash_unofficial_covid19.config import Config
from ash_unofficial_covid19.errors import ServiceError
from ash_unofficial_covid19.views import (
    AsahikawaPatientsView,
    ByAgeView,
    DailyTotalView,
    MedicalInstitutionsView,
    MonthTotalView,
    MovingAverageView,
    PerHundredThousandPopulationView
)

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    response.headers.add(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' 'unsafe-inline' \
                stackpath.bootstrapcdn.com kit.fontawesome.com; \
                script-src 'self' code.jquery.com cdnjs.cloudflare.com \
                stackpath.bootstrapcdn.com kit.fontawesome.com \
                www.googletagmanager.com \
                'nonce-Pbq-X7F-632oxHhPe6mzMC-LHYE'; \
                connect-src ka-f.fontawesome.com \
                www.google-analytics.com; \
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


def get_asahikawa_patients():
    if not hasattr(g, "asahikawa_patients"):
        g.asahikawa_patients = AsahikawaPatientsView()
    return g.asahikawa_patients


def get_medical_institutions():
    if not hasattr(g, "medical_institutions"):
        g.medical_institutions = MedicalInstitutionsView()
    return g.medical_institutions


def get_daily_total():
    if not hasattr(g, "daily_total"):
        g.daily_total = DailyTotalView()
    return g.daily_total


def get_month_total():
    if not hasattr(g, "month_total"):
        g.month_total = MonthTotalView()
    return g.month_total


def get_by_age():
    if not hasattr(g, "by_age"):
        g.by_age = ByAgeView()
    return g.by_age


def get_moving_average():
    if not hasattr(g, "moving_average"):
        g.moving_average = MovingAverageView()
    return g.moving_average


def get_per_hundred_thousand_population():
    if not hasattr(g, "per_hundred_thousand_population"):
        g.per_hundred_thousand_population = PerHundredThousandPopulationView()
    return g.per_hundred_thousand_population


@app.route("/")
def index():
    return render_template(
        "index.html",
        title="旭川市内の最新感染動向",
        gtag_id=Config.GTAG_ID,
        asahikawa_patients=get_asahikawa_patients(),
        daily_total=get_daily_total(),
        moving_average=get_moving_average(),
        per_hundred_thousand_population=get_per_hundred_thousand_population(),
        month_total=get_month_total(),
        by_age=get_by_age(),
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        title="このサイトについて",
        gtag_id=Config.GTAG_ID,
    )


@app.route("/opendata")
def opendata():
    asahikawa_patients = get_asahikawa_patients()
    results = asahikawa_patients.get_rows()
    return render_template(
        "opendata.html",
        title="非公式オープンデータ（陽性者属性CSV）",
        gtag_id=Config.GTAG_ID,
        asahikawa_patients=asahikawa_patients,
        rows=results[0].items,
        max_page=results[1],
        page=1,
    )


@app.route("/opendata/<page>")
def opendata_pages(page):
    try:
        page = int(escape(page))
    except ValueError:
        abort(404)
    try:
        asahikawa_patients = get_asahikawa_patients()
        results = asahikawa_patients.get_rows(page=page)
    except ServiceError:
        abort(404)
    max_page = results[1]
    title = "非公式オープンデータ（陽性者属性CSV）全" + str(max_page) + "ページ中" + str(page) + "ページ目"
    return render_template(
        "opendata.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        asahikawa_patients=asahikawa_patients,
        rows=results[0].items,
        max_page=max_page,
        page=page,
    )


@app.route("/medical_institutions")
def medical_institutions():
    return render_template(
        "medical_institutions.html",
        title="ワクチン接種医療機関一覧",
        gtag_id=Config.GTAG_ID,
        medical_institutions=get_medical_institutions(),
    )


@app.route("/012041_asahikawa_covid19_patients.csv")
def patients_csv():
    asahikawa_patient = get_asahikawa_patients()
    f = asahikawa_patient.get_csv()
    res = make_response()
    res.data = f.getvalue()
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "012041_asahikawa_covid19_patients.csv"
    )
    return res


@app.route("/012041_asahikawa_covid19_medical_institutions.csv")
def medical_institutions_csv():
    medical_institution = get_medical_institutions()
    f = medical_institution.get_csv()
    res = make_response()
    res.data = f.getvalue()
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "012041_asahikawa_covid19_medical_institutions.csv"
    )
    return res


@app.route("/daily_total.png")
def get_daily_total_graph():
    daily_total = get_daily_total()
    graph_image = daily_total.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "daily_total.png"
    return res


@app.route("/daily_total_for_card.png")
def get_daily_total_graph_for_card():
    daily_total = get_daily_total()
    graph_image = daily_total.get_graph_image(figsize=(6.0, 3.15))
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "daily_total_for_card.png"
    )
    return res


@app.route("/month_total.png")
def get_month_total_graph():
    month_total = get_month_total()
    graph_image = month_total.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "month_total.png"
    return res


@app.route("/by_age.png")
def get_by_age_graph():
    by_age = get_by_age()
    graph_image = by_age.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "by_age.png"
    return res


@app.route("/moving_average.png")
def get_moving_average_graph():
    moving_average = get_moving_average()
    graph_image = moving_average.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "moving_average.png"
    return res


@app.route("/per_hundred_thousand_population.png")
def get_per_hundred_thousand_population_graph():
    per_hundred_thousand_population = get_per_hundred_thousand_population()
    graph_image = per_hundred_thousand_population.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = (
        "attachment: filename=" + "per_hundred_thousand_population.png"
    )
    return res


@app.errorhandler(404)
def not_found(error):
    title = "404 Page Not Found."
    return render_template("404.html", title=title, gtag_id=Config.GTAG_ID), 404


if __name__ == "__main__":
    app.run()
