DROP TABLE IF EXISTS patients;
CREATE TABLE patients(
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
