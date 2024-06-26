import mimetypes

from flask import Flask, abort, escape, g, make_response, render_template, request

from .config import Config
from .errors import ViewError
from .services.database import ConnectionPool
from .views.outpatient import OutpatientView
from .views.patient import AsahikawaPatientView
from .views.patients_number import (
    ByAgeView,
    DailyTotalView,
    MonthlyPerAgeView,
    MonthTotalView,
    PatientsNumberView,
    PerHundredThousandPopulationView,
    WeeklyPerAgeView,
)
from .views.press_release import PressReleaseView
from .views.xml import AtomView, RssView

mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("font/otf", ".otf")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("application/javascript", ".js")
app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    csp = (
        "default-src 'self'; "
        + "style-src 'self' "
        + "unpkg.com "
        + "'unsafe-inline'; "
        + "script-src 'self' "
        + "unpkg.com www.googletagmanager.com "
        + "kit.fontawesome.com; "
        + "connect-src www.google-analytics.com ka-f.fontawesome.com; "
        + "font-src 'self' ka-f.fontawesome.com; "
        + "img-src 'self' i.creativecommons.org licensebuttons.net "
        + "data: https:; "
        + "base-uri 'self';"
    )
    response.headers.add("Content-Security-Policy", csp)
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-Frame-Options", "DENY")
    response.headers.add("X-XSS-Protection", "1;mode=block")
    return response


def get_connection():
    if "db" not in g:
        g.db = ConnectionPool()

    return g.db


@app.teardown_appcontext
def close_connection(e):
    db = g.pop("db", None)
    if db is not None:
        db.close_connection()


def get_today():
    if "today" not in g:
        conn = get_connection()
        press_release = PressReleaseView(conn)
        g.today = press_release.latest_date
    return g.today


def get_patients():
    conn = get_connection()
    return AsahikawaPatientView(conn)


def get_patients_numbers():
    conn = get_connection()
    today = get_today()
    return PatientsNumberView(today, conn)


def get_outpatients():
    conn = get_connection()
    return OutpatientView(conn)


def get_daily_total():
    conn = get_connection()
    today = get_today()
    return DailyTotalView(today, conn)


def get_month_total():
    conn = get_connection()
    today = get_today()
    return MonthTotalView(today, conn)


def get_by_age():
    conn = get_connection()
    today = get_today()
    return ByAgeView(today, conn)


def get_per_hundred_thousand_population():
    conn = get_connection()
    today = get_today()
    return PerHundredThousandPopulationView(today, conn)


def get_weekly_per_age():
    conn = get_connection()
    today = get_today()
    return WeeklyPerAgeView(today, conn)


def get_monthly_per_age():
    conn = get_connection()
    today = get_today()
    return MonthlyPerAgeView(today, conn)


def get_atom():
    conn = get_connection()
    today = get_today()
    return AtomView(today, conn)


def get_rss():
    conn = get_connection()
    today = get_today()
    return RssView(today, conn)


@app.route("/")
def index():
    return render_template(
        "index.html",
        title="トップページ",
        gtag_id=Config.GTAG_ID,
        patients_numbers=get_patients_numbers(),
        daily_total=get_daily_total(),
        monthly_per_age=get_monthly_per_age(),
        per_hundred_thousand_population=get_per_hundred_thousand_population(),
        month_total=get_month_total(),
        by_age=get_by_age(),
        leaflet=False,
    )


"""
@app.route("/past")
def past():
    return render_template(
        "past.html",
        title="旭川市内新型コロナウイルス感染症のこれまでの感染動向",
        gtag_id=Config.GTAG_ID,
        patients_numbers=get_patients_numbers(),
        daily_total=get_daily_total(),
        monthly_per_age=get_monthly_per_age(),
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
    return render_template(
        "opendata.html",
        title="非公式オープンデータ",
        gtag_id=Config.GTAG_ID,
        patients_numbers=get_patients_numbers(),
        leaflet=False,
    )


@app.route("/outpatients")
def outpatients():
    outpatients = get_outpatients()
    search_results = outpatients.find()
    last_updated = outpatients.get_last_updated().strftime("%Y年%m月%d日%H時%M分")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "outpatients.html",
        title="旭川市のコロナ発熱外来検索",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/outpatient/pediatrics")
def outpatient_pediatrics():
    outpatients = get_outpatients()
    search_results = outpatients.find(is_pediatrics=True)
    last_updated = outpatients.get_last_updated().strftime("%Y年%m月%d日%H時%M分")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "outpatient_pediatrics.html",
        title="旭川市のコロナ発熱外来一覧（小児対応可の医療機関）",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/outpatients/search_by_gps", methods=["GET", "POST"])
def outpatients_search_by_gps():
    outpatients = get_outpatients()
    last_updated = outpatients.get_last_updated().strftime("%Y年%m月%d日%H時%M分")
    if request.method == "GET":
        abort(404)

    try:
        current_latitude = escape(request.form["current_latitude"])
        current_longitude = escape(request.form["current_longitude"])
        current_latitude = float(current_latitude)
        current_longitude = float(current_longitude)
        is_pediatrics = bool(int(request.form["is_pediatrics"]))
    except (KeyError, ValueError):
        abort(400)

    title = "現在地から近い新型コロナ発熱外来の検索結果"
    try:
        if is_pediatrics:
            title += "（小児対応可の医療機関）"
            search_results = outpatients.search_by_gps(
                longitude=current_longitude, latitude=current_latitude, is_pediatrics=is_pediatrics
            )
        else:
            search_results = outpatients.search_by_gps(longitude=current_longitude, latitude=current_latitude)

    except ViewError:
        abort(500)

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "outpatient_search_by_gps.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results,
        search_lengths=search_lengths,
        current_longitude=current_longitude,
        current_latitude=current_latitude,
        is_pediatrics=is_pediatrics,
        leaflet=True,
    )


@app.route("/outpatient/medical_institution/<medical_institution>")
def outpatient_medical_institution(medical_institution):
    try:
        medical_institution = escape(medical_institution)
    except ValueError:
        abort(400)

    title = medical_institution + "の新型コロナ発熱外来情報"
    outpatients = get_outpatients()
    search_results = outpatients.find(medical_institution_name=medical_institution)
    last_updated = outpatients.get_last_updated().strftime("%Y年%m月%d日%H時%M分")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "outpatient_medical_institution.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        medical_institution=medical_institution,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/012041_asahikawa_covid19_patients.csv")
def patients_csv():
    patients = get_patients()
    csv_data = patients.get_csv()
    res = make_response()
    res.data = csv_data
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = "attachment: filename=" + "012041_asahikawa_covid19_patients.csv"
    return res


@app.route("/012041_asahikawa_covid19_daily_total.csv")
def daily_total_csv():
    patients_numbers = get_patients_numbers()
    csv_data = patients_numbers.get_daily_total_csv()
    res = make_response()
    res.data = csv_data
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = "attachment: filename=" + "012041_asahikawa_covid19_daily_total.csv"
    return res


@app.route("/api/daily_total.json")
def daily_total_json():
    patients_numbers = get_patients_numbers()
    json_data = patients_numbers.get_daily_total_json()
    res = make_response()
    res.data = json_data
    res.headers["Content-Type"] = "application/json; charset=UTF-8"
    return res


@app.route("/012041_asahikawa_covid19_daily_total_per_age.csv")
def daily_total_per_age_csv():
    patients_numbers = get_patients_numbers()
    csv_data = patients_numbers.get_daily_total_per_age_csv()
    res = make_response()
    res.data = csv_data
    res.headers["Content-Type"] = "text/csv"
    res.headers["Content-Disposition"] = "attachment: filename=" + "012041_asahikawa_covid19_daily_total_per_age.csv"
    return res


@app.route("/api/daily_total_per_age.json")
def daily_total_per_age_json():
    patients_numbers = get_patients_numbers()
    json_data = patients_numbers.get_daily_total_per_age_json()
    res = make_response()
    res.data = json_data
    res.headers["Content-Type"] = "application/json; charset=UTF-8"
    return res


@app.route("/atom.xml")
def atom_xml():
    atom = get_atom()
    last_modified = atom.get_last_modified_header()
    return (
        render_template(
            "atom.xml",
            atom=atom.get_feed(),
        ),
        200,
        {
            "Content-Type": "application/xml; charset=UTF-8",
            "Last-Modified": last_modified,
        },
    )


@app.route("/rss.xml")
def rss_xml():
    rss = get_rss()
    last_modified = rss.get_last_modified_header()
    return (
        render_template(
            "rss.xml",
            rss=rss.get_feed(),
        ),
        200,
        {
            "Content-Type": "application/xml; charset=UTF-8",
            "Last-Modified": last_modified,
        },
    )


@app.route("/sitemap.xml")
def sitemap_xml():
    sitemap = get_atom()
    last_modified = sitemap.get_last_modified_header()
    return (
        render_template(
            "sitemap.xml",
            atom=sitemap.get_feed(),
        ),
        200,
        {
            "Content-Type": "application/xml; charset=UTF-8",
            "Last-Modified": last_modified,
        },
    )


@app.route("/site.webmanifest")
def site_webmanifest():
    return render_template("site.webmanifest"), 200, {"Content-Type": "application/json; charset=UTF-8"}


@app.route("/gtag.js")
def gtag():
    return (
        render_template("gtag.js", gtag_id=Config.GTAG_ID),
        200,
        {"Content-Type": "application/javascript; charset=UTF-8"},
    )
"""


@app.errorhandler(404)
def not_found(error):
    title = "404 Page Not Found."
    message = "お探しのページは見つかりませんでした。"
    return (
        render_template(
            "error.html",
            title=title,
            message=message,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        ),
        404,
    )


@app.errorhandler(400)
def bad_request(error):
    title = "400 Bad Request."
    message = "想定外のリクエストのため処理を中断しました。"
    return (
        render_template(
            "error.html",
            title=title,
            message=message,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        ),
        400,
    )


@app.errorhandler(500)
def internal_server_error(error):
    title = "500 Internal Server Error."
    message = "何らかのエラーが原因でページを表示できません。"
    return (
        render_template(
            "error.html",
            title=title,
            message=message,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        ),
        500,
    )


if __name__ == "__main__":
    app.run()