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
    area TEXT,
    medical_institution_name VARCHAR(256) NOT NULL,
    address TEXT,
    phone_number TEXT,
    vaccine VARCHAR(256) NOT NULL,
    status TEXT,
    inoculation_time TEXT,
    target_age TEXT,
    is_target_family BOOLEAN,
    is_target_not_family BOOLEAN,
    target_other TEXT,
    memo TEXT,
    updated_at TIMESTAMPTZ NOT NULL,
    PRIMARY KEY(medical_institution_name, vaccine)
);
DROP TABLE IF EXISTS first_reservation_statuses;
CREATE TABLE first_reservation_statuses(
    id SERIAL NOT NULL,
    area TEXT,
    medical_institution_name VARCHAR(256) NOT NULL PRIMARY KEY,
    address TEXT,
    phone_number TEXT,
    vaccine VARCHAR(256),
    status TEXT,
    inoculation_time TEXT,
    target_age TEXT,
    is_target_family BOOLEAN,
    is_target_not_family BOOLEAN,
    is_target_suberb BOOLEAN,
    target_other TEXT,
    memo TEXT,
    updated_at TIMESTAMPTZ NOT NULL
);
DROP TABLE IF EXISTS patients_numbers;
CREATE TABLE patients_numbers(
    publication_date DATE NOT NULL PRIMARY KEY,
    age_under_10 INTEGER NOT NULL,
    age_10s INTEGER NOT NULL,
    age_20s INTEGER NOT NULL,
    age_30s INTEGER NOT NULL,
    age_40s INTEGER NOT NULL,
    age_50s INTEGER NOT NULL,
    age_60s INTEGER NOT NULL,
    age_70s INTEGER NOT NULL,
    age_80s INTEGER NOT NULL,
    age_over_90 INTEGER NOT NULL,
    investigating INTEGER NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
