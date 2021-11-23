DROP TABLE IF EXISTS asahikawa_patients;
CREATE TABLE asahikawa_patients(
    id SERIAL NOT NULL,
    patient_number INTEGER NOT NULL PRIMARY KEY,
    city_code CHAR(6),
    prefecture VARCHAR(16),
    city_name VARCHAR(16),
    publication_date DATE,
    onset_date DATE,
    residence TEXT,
    age VARCHAR(8),
    sex VARCHAR(4),
    occupation TEXT,
    status TEXT,
    symptom TEXT,
    overseas_travel_history BOOLEAN,
    be_discharged BOOLEAN,
    note TEXT,
    hokkaido_patient_number INTEGER,
    surrounding_status TEXT,
    close_contact TEXT,
    updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX ON asahikawa_patients (publication_date);
DROP TABLE IF EXISTS hokkaido_patients;
CREATE TABLE hokkaido_patients(
    id SERIAL NOT NULL,
    patient_number INTEGER NOT NULL PRIMARY KEY,
    city_code CHAR(6),
    prefecture VARCHAR(16),
    city_name VARCHAR(16),
    publication_date DATE,
    onset_date DATE,
    residence TEXT,
    age VARCHAR(8),
    sex VARCHAR(4),
    occupation TEXT,
    status TEXT,
    symptom TEXT,
    overseas_travel_history BOOLEAN,
    be_discharged BOOLEAN,
    note TEXT,
    updated_at TIMESTAMPTZ NOT NULL
);
DROP TABLE IF EXISTS medical_institutions;
CREATE TABLE medical_institutions(
    id SERIAL NOT NULL,
    name VARCHAR(128) NOT NULL,
    address TEXT,
    phone_number TEXT,
    book_at_medical_institution BOOLEAN,
    book_at_call_center BOOLEAN,
    area TEXT,
    memo TEXT,
    target_age VARCHAR(128),
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(name, target_age)
);
CREATE INDEX ON medical_institutions (area);
DROP TABLE IF EXISTS locations;
CREATE TABLE locations(
    id SERIAL NOT NULL,
    medical_institution_name VARCHAR(128) NOT NULL PRIMARY KEY,
    longitude FLOAT,
    latitude FLOAT,
    updated_at TIMESTAMPTZ NOT NULL
);
DROP TABLE IF EXISTS press_release_links;
CREATE TABLE press_release_links(
    id SERIAL NOT NULL,
    url VARCHAR(2083) NOT NULL,
    publication_date DATE NOT NULL PRIMARY KEY,
    updated_at TIMESTAMPTZ NOT NULL
);
DROP TABLE IF EXISTS sapporo_patients_numbers;
CREATE TABLE sapporo_patients_numbers(
    id SERIAL NOT NULL,
    publication_date DATE NOT NULL PRIMARY KEY,
    patients_number INTEGER NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
DROP TABLE IF EXISTS reservation_statuses;
CREATE TABLE reservation_statuses(
    id SERIAL NOT NULL,
    medical_institution_name VARCHAR(128) NOT NULL PRIMARY KEY,
    address TEXT,
    phone_number TEXT,
    status TEXT,
    inoculation_time TEXT,
    target_age TEXT,
    target_family BOOLEAN,
    target_not_family BOOLEAN,
    target_suberbs BOOLEAN,
    target_other TEXT,
    memo TEXT,
    updated_at TIMESTAMPTZ NOT NULL
);
DROP TABLE IF EXISTS reservation3_statuses;
CREATE TABLE reservation3_statuses(
    id SERIAL NOT NULL,
    medical_institution_name VARCHAR(128) NOT NULL PRIMARY KEY,
    address TEXT,
    phone_number TEXT,
    status TEXT,
    inoculation_time TEXT,
    target_age TEXT,
    target_family BOOLEAN,
    target_not_family BOOLEAN,
    target_suberbs BOOLEAN,
    target_other TEXT,
    memo TEXT,
    updated_at TIMESTAMPTZ NOT NULL
);
