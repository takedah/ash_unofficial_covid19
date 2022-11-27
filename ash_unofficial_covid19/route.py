import mimetypes

from flask import Flask, abort, escape, g, make_response, render_template, request

from .config import Config
from .errors import ViewError
from .services.database import ConnectionPool
from .views.child_reservation_status import ChildReservationStatusView
from .views.first_reservation_status import FirstReservationStatusView
from .views.patients_number import (
    ByAgeView,
    DailyTotalView,
    MonthTotalView,
    PatientsNumberView,
    PerHundredThousandPopulationView,
    WeeklyPerAgeView,
)
from .views.press_release import PressReleaseView
from .views.reservation_status import ReservationStatusView
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


def get_patients_numbers():
    conn = get_connection()
    today = get_today()
    return PatientsNumberView(today, conn)


def get_reservation_statuses():
    conn = get_connection()
    return ReservationStatusView(conn)


def get_first_reservation_statuses():
    conn = get_connection()
    return FirstReservationStatusView(conn)


def get_child_reservation_statuses():
    conn = get_connection()
    return ChildReservationStatusView(conn)


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
        title="旭川市内感染状況の最新動向",
        gtag_id=Config.GTAG_ID,
        patients_numbers=get_patients_numbers(),
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
    return render_template(
        "opendata.html",
        title="非公式オープンデータ",
        gtag_id=Config.GTAG_ID,
        patients_numbers=get_patients_numbers(),
        leaflet=False,
    )


@app.route("/reservation_statuses")
def reservation_statuses():
    reservation_statuses = get_reservation_statuses()
    search_results = reservation_statuses.find()
    areas = reservation_statuses.get_area_list()
    last_updated = reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_statuses.html",
        title="旭川市のコロナワクチンマップ（追加接種（オミクロン対応ワクチン））",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results.items,
        search_lengths=search_lengths,
        areas=areas,
        leaflet=True,
    )


@app.route("/reservation_statuses/search_by_gps", methods=["GET", "POST"])
def reservation_statuses_search_by_gps():
    reservation_statuses = get_reservation_statuses()
    last_updated = reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")
    if request.method == "GET":
        abort(404)

    title = "現在地から近い新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果"
    try:
        current_latitude = escape(request.form["current_latitude"])
        current_longitude = escape(request.form["current_longitude"])
        current_latitude = float(current_latitude)
        current_longitude = float(current_longitude)
    except (KeyError, ValueError):
        abort(400)

    try:
        search_results = reservation_statuses.search_by_gps(longitude=current_longitude, latitude=current_latitude)
    except ViewError:
        abort(500)

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_status_search_by_gps.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results,
        search_lengths=search_lengths,
        current_longitude=current_longitude,
        current_latitude=current_latitude,
        leaflet=True,
    )


@app.route("/first_reservation_statuses/search_by_gps", methods=["GET", "POST"])
def first_reservation_statuses_search_by_gps():
    first_reservation_statuses = get_first_reservation_statuses()
    last_updated = first_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")
    if request.method == "GET":
        abort(404)

    title = "現在地から近い新型コロナワクチン接種医療機関（1・2回目接種）の検索結果"
    try:
        current_latitude = escape(request.form["current_latitude"])
        current_longitude = escape(request.form["current_longitude"])
        current_latitude = float(current_latitude)
        current_longitude = float(current_longitude)
    except (KeyError, ValueError):
        abort(400)

    try:
        search_results = first_reservation_statuses.search_by_gps(
            longitude=current_longitude, latitude=current_latitude
        )
    except ViewError:
        abort(500)

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_status_search_by_gps.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results,
        search_lengths=search_lengths,
        current_longitude=current_longitude,
        current_latitude=current_latitude,
        leaflet=True,
    )


@app.route("/child_reservation_statuses/search_by_gps", methods=["GET", "POST"])
def child_reservation_statuses_search_by_gps():
    child_reservation_statuses = get_child_reservation_statuses()
    last_updated = child_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")
    if request.method == "GET":
        abort(404)

    title = "現在地から近い新型コロナワクチン接種医療機関（5歳から11歳接種）の検索結果"
    try:
        current_latitude = escape(request.form["current_latitude"])
        current_longitude = escape(request.form["current_longitude"])
        current_latitude = float(current_latitude)
        current_longitude = float(current_longitude)
    except (KeyError, ValueError):
        abort(400)

    try:
        search_results = child_reservation_statuses.search_by_gps(
            longitude=current_longitude, latitude=current_latitude
        )
    except ViewError:
        abort(500)

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_status_search_by_gps.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results,
        search_lengths=search_lengths,
        current_longitude=current_longitude,
        current_latitude=current_latitude,
        leaflet=True,
    )


@app.route("/reservation_status/area/<area>")
def reservation_status_area(area):
    try:
        area = escape(area)
    except ValueError:
        abort(400)

    reservation_statuses = get_reservation_statuses()
    search_results = reservation_statuses.find(area=area)
    last_updated = reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_status_area.html",
        title=area + "の新型コロナワクチン接種医療機関（追加接種（オミクロン対応ワクチン））の検索結果",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        area=area,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/reservation_status/medical_institution/<medical_institution>")
def reservation_status_medical_institution(medical_institution):
    try:
        medical_institution = escape(medical_institution)
    except ValueError:
        abort(400)

    reservation_statuses = get_reservation_statuses()
    search_results = reservation_statuses.find(medical_institution_name=medical_institution)
    last_updated = reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_status_medical_institution.html",
        title=medical_institution + "の新型コロナワクチン接種予約受付状況（追加接種（オミクロン対応ワクチン））",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        medical_institution=medical_institution,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/first_reservation_statuses")
def first_reservation_statuses():
    first_reservation_statuses = get_first_reservation_statuses()
    search_results = first_reservation_statuses.find()
    areas = first_reservation_statuses.get_area_list()
    last_updated = first_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_statuses.html",
        title="旭川市のコロナワクチンマップ（1・2回目接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results.items,
        search_lengths=search_lengths,
        areas=areas,
        leaflet=True,
    )


@app.route("/first_reservation_status/area/<area>")
def first_reservation_status_area(area):
    try:
        area = escape(area)
    except ValueError:
        abort(400)

    first_reservation_statuses = get_first_reservation_statuses()
    search_results = first_reservation_statuses.find(area=area)
    last_updated = first_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_status_area.html",
        title=area + "の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        area=area,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/first_reservation_status/medical_institution/<medical_institution>")
def first_reservation_status_medical_institution(medical_institution):
    try:
        medical_institution = escape(medical_institution)
    except ValueError:
        abort(400)

    first_reservation_statuses = get_first_reservation_statuses()
    search_results = first_reservation_statuses.find(medical_institution_name=medical_institution)
    last_updated = first_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_status_medical_institution.html",
        title=medical_institution + "の新型コロナワクチン接種予約受付状況（1・2回目接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        medical_institution=medical_institution,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/child_reservation_statuses")
def child_reservation_statuses():
    child_reservation_statuses = get_child_reservation_statuses()
    search_results = child_reservation_statuses.find()
    areas = child_reservation_statuses.get_area_list()
    last_updated = child_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_statuses.html",
        title="旭川市のコロナワクチンマップ（5歳から11歳接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        search_results=search_results.items,
        search_lengths=search_lengths,
        areas=areas,
        leaflet=True,
    )


@app.route("/child_reservation_status/area/<area>")
def child_reservation_status_area(area):
    try:
        area = escape(area)
    except ValueError:
        abort(400)

    child_reservation_statuses = get_child_reservation_statuses()
    search_results = child_reservation_statuses.find(area=area)
    last_updated = child_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_status_area.html",
        title=area + "の新型コロナワクチン接種医療機関（5歳から11歳接種）の検索結果",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        area=area,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/child_reservation_status/medical_institution/<medical_institution>")
def child_reservation_status_medical_institution(medical_institution):
    try:
        medical_institution = escape(medical_institution)
    except ValueError:
        abort(400)

    child_reservation_statuses = get_child_reservation_statuses()
    search_results = child_reservation_statuses.find(medical_institution_name=medical_institution)
    last_updated = child_reservation_statuses.get_last_updated().strftime("%Y/%m/%d %H:%M")

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_status_medical_institution.html",
        title=medical_institution + "の新型コロナワクチン接種予約受付状況（5歳から11歳接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=last_updated,
        medical_institution=medical_institution,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


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


@app.route("/api/reservation_status.json")
def reservation_status_json():
    reservation_statuses = get_reservation_statuses()
    json_data = reservation_statuses.get_reservation_status_json()
    res = make_response()
    res.data = json_data
    res.headers["Content-Type"] = "application/json; charset=UTF-8"
    return res


@app.route("/api/first_reservation_status.json")
def first_reservation_status_json():
    first_reservation_statuses = get_first_reservation_statuses()
    json_data = first_reservation_statuses.get_reservation_status_json()
    res = make_response()
    res.data = json_data
    res.headers["Content-Type"] = "application/json; charset=UTF-8"
    return res


@app.route("/api/child_reservation_status.json")
def child_reservation_status_json():
    child_reservation_statuses = get_child_reservation_statuses()
    json_data = child_reservation_statuses.get_reservation_status_json()
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
