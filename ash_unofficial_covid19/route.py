from flask import Flask, abort, escape, g, make_response, render_template, request

from .config import Config
from .errors import DataModelError, ServiceError
from .views.child_reservation_status import ChildReservationStatusView
from .views.first_reservation_status import FirstReservationStatusView
from .views.graph import ByAgeView, DailyTotalView, MonthTotalView, PerHundredThousandPopulationView, WeeklyPerAgeView
from .views.patient import AsahikawaPatientView
from .views.patients_number import PatientsNumberView
from .views.reservation_status import ReservationStatusView
from .views.xml import AtomView, RssView

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    csp = (
        "default-src 'self'; "
        + "style-src 'self' "
        + "stackpath.bootstrapcdn.com unpkg.com "
        + "fonts.googleapis.com "
        + "'unsafe-inline'; "
        + "script-src 'self' "
        + "code.jquery.com cdnjs.cloudflare.com stackpath.bootstrapcdn.com "
        + "unpkg.com www.googletagmanager.com www.line-website.com "
        + "kit.fontawesome.com "
        + "'nonce-Pbq-X7F-632oxHhPe6mzMC-LHYE'; "
        + "connect-src www.google-analytics.com ka-f.fontawesome.com "
        + "l.typesquare.com; "
        + "font-src ka-f.fontawesome.com fonts.gstatic.com; "
        + "img-src 'self' i.creativecommons.org licensebuttons.net "
        + "data: https:; "
        + "frame-src docs.google.com;"
    )
    response.headers.add("Content-Security-Policy", csp)
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-Frame-Options", "DENY")
    response.headers.add("X-XSS-Protection", "1;mode=block")
    return response


def get_asahikawa_patients():
    g.asahikawa_patients = AsahikawaPatientView()
    return g.asahikawa_patients


def get_patients_numbers():
    g.patients_numbers = PatientsNumberView()
    return g.patients_numbers


def get_reservation_statuses():
    g.reservation_statuses = ReservationStatusView()
    return g.reservation_statuses


def get_first_reservation_statuses():
    g.first_reservation_statuses = FirstReservationStatusView()
    return g.first_reservation_statuses


def get_child_reservation_statuses():
    g.child_reservation_statuses = ChildReservationStatusView()
    return g.child_reservation_statuses


def get_daily_total():
    g.daily_total = DailyTotalView()
    return g.daily_total


def get_month_total():
    g.month_total = MonthTotalView()
    return g.month_total


def get_by_age():
    g.by_age = ByAgeView()
    return g.by_age


def get_per_hundred_thousand_population():
    g.per_hundred_thousand_population = PerHundredThousandPopulationView()
    return g.per_hundred_thousand_population


def get_weekly_per_age():
    g.weekly_per_age = WeeklyPerAgeView()
    return g.weekly_per_age


def get_atom():
    g.atom = AtomView()
    return g.atom


def get_rss():
    g.rss = RssView()
    return g.rss


@app.route("/")
def index():
    patients_numbers = get_patients_numbers()
    return render_template(
        "index.html",
        title="旭川市内感染状況の最新動向",
        gtag_id=Config.GTAG_ID,
        last_updated=patients_numbers.last_updated,
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
    patients_numbers = get_patients_numbers()
    return render_template(
        "opendata.html",
        title="非公式オープンデータ",
        gtag_id=Config.GTAG_ID,
        last_updated=patients_numbers.last_updated,
        leaflet=False,
    )


@app.route("/patients")
def patients():
    asahikawa_patients = get_asahikawa_patients()
    results = asahikawa_patients.find()
    return render_template(
        "patients.html",
        title="感染者の状況",
        gtag_id=Config.GTAG_ID,
        last_updated=asahikawa_patients.last_updated,
        patients=results[0],
        max_page=results[1],
        page=1,
        leaflet=False,
    )


@app.route("/patients/<page>")
def patients_pages(page):
    try:
        page = int(escape(page))
    except ValueError:
        abort(404)
    try:
        asahikawa_patients = get_asahikawa_patients()
        results = asahikawa_patients.find(page=page)
    except ServiceError:
        abort(404)
    title = "感染者の状況（非公式オープンデータ）全" + str(results[1]) + "ページ中" + str(page) + "ページ目"
    return render_template(
        "patients.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=asahikawa_patients.last_updated,
        patients=results[0],
        max_page=results[1],
        page=page,
        leaflet=False,
    )


@app.route("/reservation_statuses")
def reservation_statuses():
    reservation_statuses = get_reservation_statuses()
    search_results = reservation_statuses.find()
    areas = reservation_statuses.get_area_list()

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_statuses.html",
        title="コロナワクチンマップ（3回目接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=reservation_statuses.last_updated,
        search_results=search_results.items,
        search_lengths=search_lengths,
        areas=areas,
        leaflet=True,
    )


@app.route("/reservation_statuses/search_by_gps", methods=["GET", "POST"])
def reservation_statuses_search_by_gps():
    reservation_statuses = get_reservation_statuses()
    if request.method == "GET":
        search_results = reservation_statuses.find()
        areas = reservation_statuses.get_areas()
        search_lengths = len(search_results.items)
        if search_lengths == 0:
            abort(404)

        return render_template(
            "reservation_statuses.html",
            title="コロナワクチンマップ（3回目接種）",
            gtag_id=Config.GTAG_ID,
            last_updated=reservation_statuses.last_updated,
            search_results=search_results.items,
            search_lengths=search_lengths,
            areas=areas.items,
            leaflet=True,
        )

    title = "現在地から近い新型コロナワクチン接種医療機関（3回目接種）の検索結果"
    current_latitude = escape(request.form["current_latitude"])
    current_longitude = escape(request.form["current_longitude"])
    try:
        current_latitude = float(current_latitude)
        current_longitude = float(current_longitude)
    except ValueError:
        title = "緯度経度が正しく指定されていません"
        return render_template(
            "error.html",
            title=title,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        )

    try:
        search_results = reservation_statuses.search_by_gps(longitude=current_longitude, latitude=current_latitude)
    except DataModelError as e:
        title = e.message
        return render_template(
            "error.html",
            title=title,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        )

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_status_search_by_gps.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=reservation_statuses.last_updated,
        search_results=search_results,
        search_lengths=search_lengths,
        current_longitude=current_longitude,
        current_latitude=current_latitude,
        leaflet=True,
    )


@app.route("/first_reservation_statuses/search_by_gps", methods=["GET", "POST"])
def first_reservation_statuses_search_by_gps():
    first_reservation_statuses = get_first_reservation_statuses()
    if request.method == "GET":
        search_results = first_reservation_statuses.find()
        areas = first_reservation_statuses.get_areas()
        search_lengths = len(search_results.items)
        if search_lengths == 0:
            abort(404)

        return render_template(
            "first_reservation_statuses.html",
            title="コロナワクチンマップ（1・2回目接種）",
            gtag_id=Config.GTAG_ID,
            last_updated=first_reservation_statuses.last_updated,
            search_results=search_results.items,
            search_lengths=search_lengths,
            areas=areas.items,
            leaflet=True,
        )

    title = "現在地から近い新型コロナワクチン接種医療機関（1・2回目接種）の検索結果"
    current_latitude = escape(request.form["current_latitude"])
    current_longitude = escape(request.form["current_longitude"])
    try:
        current_latitude = float(current_latitude)
        current_longitude = float(current_longitude)
    except ValueError:
        title = "緯度経度が正しく指定されていません"
        return render_template(
            "error.html",
            title=title,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        )

    try:
        search_results = first_reservation_statuses.search_by_gps(
            longitude=current_longitude, latitude=current_latitude
        )
    except DataModelError as e:
        title = e.message
        return render_template(
            "error.html",
            title=title,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        )

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_status_search_by_gps.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=first_reservation_statuses.last_updated,
        search_results=search_results,
        search_lengths=search_lengths,
        current_longitude=current_longitude,
        current_latitude=current_latitude,
        leaflet=True,
    )


@app.route("/child_reservation_statuses/search_by_gps", methods=["GET", "POST"])
def child_reservation_statuses_search_by_gps():
    child_reservation_statuses = get_child_reservation_statuses()
    if request.method == "GET":
        search_results = child_reservation_statuses.find()
        areas = child_reservation_statuses.get_areas()
        search_lengths = len(search_results.items)
        if search_lengths == 0:
            abort(404)

        return render_template(
            "child_reservation_statuses.html",
            title="コロナワクチンマップ（5歳から11歳接種）",
            gtag_id=Config.GTAG_ID,
            last_updated=child_reservation_statuses.last_updated,
            search_results=search_results.items,
            search_lengths=search_lengths,
            areas=areas.items,
            leaflet=True,
        )

    title = "現在地から近い新型コロナワクチン接種医療機関（5歳から11歳接種）の検索結果"
    current_latitude = escape(request.form["current_latitude"])
    current_longitude = escape(request.form["current_longitude"])
    try:
        current_latitude = float(current_latitude)
        current_longitude = float(current_longitude)
    except ValueError:
        title = "緯度経度が正しく指定されていません"
        return render_template(
            "error.html",
            title=title,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        )

    try:
        search_results = child_reservation_statuses.search_by_gps(
            longitude=current_longitude, latitude=current_latitude
        )
    except DataModelError as e:
        title = e.message
        return render_template(
            "error.html",
            title=title,
            gtag_id=Config.GTAG_ID,
            leaflet=False,
        )

    search_lengths = len(search_results)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_status_search_by_gps.html",
        title=title,
        gtag_id=Config.GTAG_ID,
        last_updated=child_reservation_statuses.last_updated,
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
        abort(404)

    reservation_statuses = get_reservation_statuses()
    search_results = reservation_statuses.find(area=area)

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_status_area.html",
        title=area + "の新型コロナワクチン接種医療機関（3回目接種）の検索結果",
        gtag_id=Config.GTAG_ID,
        last_updated=reservation_statuses.last_updated,
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
        abort(404)

    reservation_statuses = get_reservation_statuses()
    search_results = reservation_statuses.find(medical_institution_name=medical_institution)

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "reservation_status_medical_institution.html",
        title=medical_institution + "の新型コロナワクチン接種予約受付状況（3回目接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=reservation_statuses.last_updated,
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

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_statuses.html",
        title="コロナワクチンマップ（1・2回目接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=first_reservation_statuses.last_updated,
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
        abort(404)

    first_reservation_statuses = get_first_reservation_statuses()
    search_results = first_reservation_statuses.find(area=area)

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_status_area.html",
        title=area + "の新型コロナワクチン接種医療機関（1・2回目接種）の検索結果",
        gtag_id=Config.GTAG_ID,
        last_updated=first_reservation_statuses.last_updated,
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
        abort(404)

    first_reservation_statuses = get_first_reservation_statuses()
    search_results = first_reservation_statuses.find(medical_institution_name=medical_institution)

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "first_reservation_status_medical_institution.html",
        title=medical_institution + "の新型コロナワクチン接種予約受付状況（1・2回目接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=first_reservation_statuses.last_updated,
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

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_statuses.html",
        title="コロナワクチンマップ（5歳から11歳接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=child_reservation_statuses.last_updated,
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
        abort(404)

    child_reservation_statuses = get_child_reservation_statuses()
    search_results = child_reservation_statuses.find(area=area)

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_status_area.html",
        title=area + "の新型コロナワクチン接種医療機関（5歳から11歳接種）の検索結果",
        gtag_id=Config.GTAG_ID,
        last_updated=child_reservation_statuses.last_updated,
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
        abort(404)

    child_reservation_statuses = get_child_reservation_statuses()
    search_results = child_reservation_statuses.find(medical_institution_name=medical_institution)

    search_lengths = len(search_results.items)
    if search_lengths == 0:
        abort(404)

    return render_template(
        "child_reservation_status_medical_institution.html",
        title=medical_institution + "の新型コロナワクチン接種予約受付状況（5歳から11歳接種）",
        gtag_id=Config.GTAG_ID,
        last_updated=child_reservation_statuses.last_updated,
        medical_institution=medical_institution,
        search_results=search_results.items,
        search_lengths=search_lengths,
        leaflet=True,
    )


@app.route("/012041_asahikawa_covid19_patients.csv")
def patients_csv():
    asahikawa_patient = get_asahikawa_patients()
    csv_data = asahikawa_patient.get_csv()
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


@app.route("/daily_total.png")
def get_daily_total_graph():
    daily_total = get_daily_total()
    graph_image = daily_total.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "image/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "daily_total.png"
    return res


@app.route("/daily_total_for_card.png")
def get_daily_total_graph_for_card():
    daily_total = get_daily_total()
    graph_image = daily_total.get_graph_image(figsize=(6.0, 3.15))
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "image/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "daily_total_for_card.png"
    return res


@app.route("/month_total.png")
def get_month_total_graph():
    month_total = get_month_total()
    graph_image = month_total.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "image/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "month_total.png"
    return res


@app.route("/month_total_for_card.png")
def get_month_total_graph_for_card():
    month_total = get_month_total()
    graph_image = month_total.get_graph_image(figsize=(6.0, 3.15))
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "image/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "month_total_for_card.png"
    return res


@app.route("/by_age.png")
def get_by_age_graph():
    by_age = get_by_age()
    graph_image = by_age.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "image/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "by_age.png"
    return res


@app.route("/per_hundred_thousand_population.png")
def get_per_hundred_thousand_population_graph():
    per_hundred_thousand_population = get_per_hundred_thousand_population()
    graph_image = per_hundred_thousand_population.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "image/png"
    res.headers["Content-Disposition"] = "attachment: filename=" + "per_hundred_thousand_population.png"
    return res


@app.route("/weekly_per_age.png")
def get_weekly_per_age_graph():
    weekly_per_age = get_weekly_per_age()
    graph_image = weekly_per_age.get_graph_image()
    res = make_response()
    res.data = graph_image.getvalue()
    res.headers["Content-Type"] = "image/png"
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


if __name__ == "__main__":
    app.run()
