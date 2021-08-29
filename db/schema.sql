DROP TABLE IF EXISTS asahikawa_patients;
CREATE TABLE asahikawa_patients(
    id SERIAL PRIMARY KEY NOT NULL,
    patient_number INTEGER UNIQUE NOT NULL,
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
DROP TABLE IF EXISTS hokkaido_patients;
CREATE TABLE hokkaido_patients(
    id SERIAL PRIMARY KEY NOT NULL,
    patient_number INTEGER UNIQUE NOT NULL,
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
DROP TABLE IF EXISTS locations;
CREATE TABLE locations(
    id SERIAL PRIMARY KEY NOT NULL,
    medical_institution_name VARCHAR(128) UNIQUE NOT NULL,
    longitude FLOAT,
    latitude FLOAT,
    updated_at TIMESTAMPTZ NOT NULL
);
DROP TABLE IF EXISTS press_release_links;
CREATE TABLE press_release_links(
    id SERIAL PRIMARY KEY NOT NULL,
    url VARCHAR(2083) UNIQUE NOT NULL,
    publication_date DATE NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);
