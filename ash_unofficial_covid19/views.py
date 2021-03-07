import csv
import io
import os

from flask import Flask, g, make_response, render_template, url_for

from ash_unofficial_covid19.db import DB
from ash_unofficial_covid19.services import AsahikawaPatientService

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
                img-src i.creativecommons.org licensebuttons.net;",
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


def connect_db():
    return DB()


def get_db():
    if not hasattr(g, "postgres_db"):
        g.postgres_db = connect_db()
    return g.postgres_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "postgres_db"):
        g.postgres_db.close()


@app.route("/")
def index():
    patient_service = AsahikawaPatientService(get_db())
    title = "旭川市コロナウイルス感染症非公式オープンデータ"
    last_updated = patient_service.get_last_updated()
    return render_template(
        "index.html",
        title=title,
        last_updated=last_updated.strftime("%Y/%m/%d %H:%M"),
    )


@app.route("/012041_asahikawa_covid19_patients.csv")
def patients_csv():
    patient_service = AsahikawaPatientService(get_db())
    patients_rows = patient_service.get_patients_rows()
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


@app.errorhandler(404)
def not_found(error):
    title = "404 Page Not Found."
    return render_template("404.html", title=title)


if __name__ == "__main__":
    app.run(debug=True)
