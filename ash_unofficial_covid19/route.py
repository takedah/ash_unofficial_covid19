import os

from flask import Flask, abort, escape, g, make_response, render_template, url_for
from flask_caching import Cache

from .config import Config
from .errors import ServiceError
from .views.view import (
    AsahikawaPatientsView,
    ByAgeView,
    DailyTotalView,
    MedicalInstitutionsView,
    MonthTotalView,
    MovingAverageView,
    PerHundredThousandPopulationView,
    WeeklyPerAgeView,
)

cache = Cache(config={"CACHE_TYPE": "simple"})
app = Flask(__name__)
cache.init_app(app)


@app.after_request
def add_security_headers(response):
    csp = (
        "default-src 'self'; "
        + "style-src 'self' 'unsafe-inline' "
        + "stackpath.bootstrapcdn.com unpkg.com kit.fontawesome.com; "
        + "script-src 'self' "
        + "code.jquery.com cdnjs.cloudflare.com stackpath.bootstrapcdn.com "
        + "unpkg.com kit.fontawesome.com www.googletagmanager.com minmoji.ucda.jp "
        + "'nonce-Pbq-X7F-632oxHhPe6mzMC-LHYE'; "
        + "connect-src ka-f.fontawesome.com www.google-analytics.com; "
        + "font-src ka-f.fontawesome.com minmoji.ucda.jp; "
        + "img-src 'self' i.creativecommons.org licensebuttons.net "
        + "data: https:"
    )
    response.headers.add("Content-Security-Policy", csp)
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


@cache.cached(timeout=180, key_prefix="asahikawa_patients")
def get_asahikawa_patients():
    g.asahikawa_patients = AsahikawaPatientsView()
    return g.asahikawa_patients


@cache.cached(timeout=180, key_prefix="medical_institutions")
def get_medical_institutions():
    g.medical_institutions = MedicalInstitutionsView()
    return g.medical_institutions


@cache.cached(timeout=180, key_prefix="daily_total")
def get_daily_total():
    g.daily_total = DailyTotalView()
    return g.daily_total


@cache.cached(timeout=180, key_prefix="month_total")
def get_month_total():
    g.month_total = MonthTotalView()
    return g.month_total


@cache.cached(timeout=180, key_prefix="by_age")
def get_by_age():
    g.by_age = ByAgeView()
    return g.by_age


@cache.cached(timeout=180, key_prefix="moving_average")
def get_moving_average():
    g.moving_average = MovingAverageView()
    return g.moving_average


@cache.cached(timeout=180, key_prefix="per_hundred_thousand_population")
def get_per_hundred_thousand_population():
    g.per_hundred_thousand_population = PerHundredThousandPopulationView()
    return g.per_hundred_thousand_population


@cache.cached(timeout=180, key_prefix="weekly_per_age")
def get_weekly_per_age():
    g.weekly_per_age = WeeklyPerAgeView()
    return g.weekly_per_age


@app.route("/")
def index():
    return render_template(
        "index.html",
        title="旭川市内感染状況の最新動向",
        gtag_id=Config.GTAG_ID,
        asahikawa_patients=get_asahikawa_patients(),
        daily_total=get_daily_total(),
        weekly_per_age=get_weekly_per_age(),
        per_hundred_thousand_population=get_per_hundred_thousand_population(),
        month_total=get_month_total(),
        by_age=get_by_age(),
        leaflet=False,
    )


@app.route("/about")
def about():
    return render_template(
        "about.html",
        title="このサイトについて",
        gtag_id=Config.GTAG_ID,
        leaflet=False,
    )


@app.route("/opendata")
def opendata():
    asahikawa_patients = get_asahikawa_patients()
    results = asahikawa_patients.get_rows()
    return render_template(
        "opendata.html",
        title="感染者の状況（非公式オープンデータ）",
        gtag_id=Config.GTAG_ID,
        last_updated=asahikawa_patients.last_updated,
        patients=results[0],
        max_page=results[1],
        page=1,
        leaflet=False,
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
    title = "感染者の状況（非公式オープンデータ）全" + str(results[1]) + "ページ中" + str(page) + "ページ目"
    return render_template(
        "opendata.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=asahikawa_patients.last_updated,
        patients=results[0],
        max_page=results[1],
        page=page,
        leaflet=False,
    )


@app.route("/medical_institutions")
def medical_institutions():
    medical_institutions = get_medical_institutions()
    above_16_medical_institutions = medical_institutions.find_area()
    below_15_medical_institutions = medical_institutions.find_area(is_pediatric=True)
    return render_template(
        "medical_institutions.html",
        title="新型コロナワクチン接種医療機関一覧",
        gtag_id=Config.GTAG_ID,
        last_updated=medical_institutions.last_updated,
        above_16_medical_institutions=above_16_medical_institutions,
        above_16_medical_institutions_number=len(above_16_medical_institutions),
        below_15_medical_institutions=below_15_medical_institutions,
        below_15_medical_institutions_number=len(below_15_medical_institutions),
        above_16_area_list=medical_institutions.get_area_list(),
        below_15_area_list=medical_institutions.get_area_list(is_pediatric=True),
        leaflet=True,
    )


@app.route("/medical_institutions/areas/<area>")
def medical_institutions_areas(area):
    medical_institutions = get_medical_institutions()
    try:
        area = escape(area)
    except ValueError:
        abort(404)

    try:
        search_results = medical_institutions.find_area(area=area)
    except ServiceError:
        abort(404)

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "area.html",
        title="【旭川市】" + area + "の新型コロナワクチン接種医療機関一覧（16歳以上）",
        gtag_id=Config.GTAG_ID,
        reservation_status_updated=medical_institutions.reservation_status_updated,
        area=area,
        search_results=search_results,
        search_lengths=search_lengths,
        above_16_area_list=medical_institutions.get_area_list(),
        below_15_area_list=medical_institutions.get_area_list(is_pediatric=True),
        is_pediatric=False,
        leaflet=True,
    )


@app.route("/medical_institutions/areas/pediatrics/<area>")
def pediatric_medical_institutions_areas(area):
    medical_institutions = get_medical_institutions()
    try:
        area = escape(area)
    except ValueError:
        abort(404)

    try:
        search_results = medical_institutions.find_area(area=area, is_pediatric=True)
    except ServiceError:
        abort(404)

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "area.html",
        title="【旭川市】" + area + "の新型コロナワクチン接種医療機関一覧（12歳から15歳まで）",
        gtag_id=Config.GTAG_ID,
        reservation_status_updated=medical_institutions.reservation_status_updated,
        area=area,
        search_results=search_results,
        search_lengths=search_lengths,
        above_16_area_list=medical_institutions.get_area_list(),
        below_15_area_list=medical_institutions.get_area_list(is_pediatric=True),
        is_pediatric=True,
        leaflet=True,
    )


@app.route("/medical_institution/<name>")
def medical_institution(name):
    medical_institutions = get_medical_institutions()
    try:
        name = escape(name)
    except ValueError:
        abort(404)

    try:
        medical_institution = medical_institutions.find(name=name)
    except ServiceError:
        abort(404)

    return render_template(
        "medical_institution.html",
        title="【旭川市のワクチン接種医療機関】" + name + "（16歳以上）",
        gtag_id=Config.GTAG_ID,
        reservation_status_updated=medical_institutions.reservation_status_updated,
        medical_institution=medical_institution,
        above_16_area_list=medical_institutions.get_area_list(),
        below_15_area_list=medical_institutions.get_area_list(is_pediatric=True),
        is_pediatric=False,
        leaflet=True,
    )


@app.route("/medical_institution/pediatrics/<name>")
def pediatric_medical_institution(name):
    medical_institutions = get_medical_institutions()
    try:
        name = escape(name)
    except ValueError:
        abort(404)

    try:
        medical_institution = medical_institutions.find(name=name, is_pediatric=True)
    except ServiceError:
        abort(404)

    return render_template(
        "medical_institution.html",
        title="【旭川市のワクチン接種医療機関】" + name + "（12歳から15歳まで）",
        gtag_id=Config.GTAG_ID,
        reservation_status_updated=medical_institutions.reservation_status_updated,
        medical_institution=medical_institution,
        above_16_area_list=medical_institutions.get_area_list(),
        below_15_area_list=medical_institutions.get_area_list(is_pediatric=True),
        is_pediatric=True,
        leaflet=True,
    )


@app.route("/012041_asahikawa_covid19_patients.csv")
def patients_csv():
    asahikawa_patient = get_asahikawa_patients()
    f = asahikawa_patient.get_csv()
    res = make_response()
    res.data = f.getvalue()
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = "attachment: filename=" + "012041_asahikawa_covid19_patients.csv"
    return res


@app.route("/012041_asahikawa_covid19_medical_institutions.csv")
def medical_institutions_csv():
    medical_institution = get_medical_institutions()
    f = medical_institution.get_csv()
    res = make_response()
    res.data = f.getvalue()
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = "attachment: filename=" + "012041_asahikawa_covid19_medical_institutions.csv"
    return res


@app.route("/daily_total.png")
@cache.cached(timeout=180)
def get_daily_total_graph():
    daily_total = get_daily_total()
    graph_image = daily_total.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "daily_total.png"
    return res


@app.route("/daily_total_for_card.png")
@cache.cached(timeout=180)
def get_daily_total_graph_for_card():
    daily_total = get_daily_total()
    graph_image = daily_total.get_graph_image(figsize=(6.0, 3.15))
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "daily_total_for_card.png"
    return res


@app.route("/month_total.png")
@cache.cached(timeout=180)
def get_month_total_graph():
    month_total = get_month_total()
    graph_image = month_total.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "month_total.png"
    return res


@app.route("/by_age.png")
@cache.cached(timeout=180)
def get_by_age_graph():
    by_age = get_by_age()
    graph_image = by_age.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "by_age.png"
    return res


@app.route("/moving_average.png")
@cache.cached(timeout=180)
def get_moving_average_graph():
    moving_average = get_moving_average()
    graph_image = moving_average.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "moving_average.png"
    return res


@app.route("/per_hundred_thousand_population.png")
@cache.cached(timeout=180)
def get_per_hundred_thousand_population_graph():
    per_hundred_thousand_population = get_per_hundred_thousand_population()
    graph_image = per_hundred_thousand_population.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "per_hundred_thousand_population.png"
    return res


@app.route("/weekly_per_age.png")
@cache.cached(timeout=180)
def get_weekly_per_age_graph():
    weekly_per_age = get_weekly_per_age()
    graph_image = weekly_per_age.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "img/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "weekly_per_age.png"
    return res


@app.errorhandler(404)
def not_found(error):
    title = "404 Page Not Found."
    return (
        render_template(
            "404.html",
            title=title,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        ),
        404,
    )


if __name__ == "__main__":
    app.run()
