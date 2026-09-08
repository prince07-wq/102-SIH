-- Creates the PostgreSQL objects required by the MPLADS runtime backend.
-- Run this script against the target MPLADS database before importing projects.

BEGIN;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE IF NOT EXISTS projects (
    project_id BIGINT PRIMARY KEY,
    activity_name TEXT,
    work_category TEXT,
    work_description TEXT,
    state_name TEXT,
    constituency TEXT,
    mp_name TEXT,
    ida_name TEXT,
    recommendation_date DATE,
    sanction_date DATE,
    sanction_amount DOUBLE PRECISION,
    work_stage TEXT,
    tenure TEXT,
    house_of_parliament INTEGER,
    has_expenditure BOOLEAN,
    expenditure_record_count INTEGER,
    total_disbursed DOUBLE PRECISION,
    unique_vendor_count INTEGER,
    first_expenditure_date DATE,
    last_expenditure_date DATE,
    has_official_attachment BOOLEAN,
    overall_score DOUBLE PRECISION,
    risk_level TEXT,
    flag_count INTEGER,
    base_score DOUBLE PRECISION,
    strongest_detector TEXT,
    multi_signal_bonus INTEGER,
    score_capped BOOLEAN,
    ml_eligible BOOLEAN,
    ml_status TEXT,
    ml_raw_score DOUBLE PRECISION,
    ml_anomaly_value DOUBLE PRECISION,
    ml_anomaly_score DOUBLE PRECISION,
    ml_is_anomaly BOOLEAN,
    ml_anomaly_level TEXT,
    ml_rule_agreement TEXT,
    ml_project_age_days INTEGER,
    ml_days_to_first_expenditure INTEGER,
    ml_expenditure_record_count INTEGER,
    ml_unique_vendor_count INTEGER,
    ml_disbursement_ratio DOUBLE PRECISION,
    ml_work_stage TEXT,
    details JSONB NOT NULL,
    vendor_names TEXT,
    work_ids_text TEXT
);

CREATE INDEX IF NOT EXISTS idx_projects_state
    ON projects (state_name);

CREATE INDEX IF NOT EXISTS idx_projects_constituency
    ON projects (constituency);

CREATE INDEX IF NOT EXISTS idx_projects_risk_level
    ON projects (risk_level);

CREATE INDEX IF NOT EXISTS idx_projects_overall_score
    ON projects (overall_score);

CREATE INDEX IF NOT EXISTS idx_projects_work_stage
    ON projects (work_stage);

CREATE INDEX IF NOT EXISTS idx_projects_ml_eligible
    ON projects (ml_eligible);

CREATE INDEX IF NOT EXISTS idx_projects_ml_anomaly
    ON projects (ml_is_anomaly);

CREATE INDEX IF NOT EXISTS idx_projects_ml_level
    ON projects (ml_anomaly_level);

CREATE INDEX IF NOT EXISTS idx_projects_ml_agreement
    ON projects (ml_rule_agreement);

CREATE INDEX IF NOT EXISTS idx_projects_ml_score
    ON projects (ml_anomaly_score);

CREATE INDEX IF NOT EXISTS idx_projects_description_trgm
    ON projects USING GIN (work_description gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_activity_trgm
    ON projects USING GIN (activity_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_mp_trgm
    ON projects USING GIN (mp_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_authority_trgm
    ON projects USING GIN (ida_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_constituency_trgm
    ON projects USING GIN (constituency gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_state_trgm
    ON projects USING GIN (state_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_vendor_names_trgm
    ON projects USING GIN (vendor_names gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_projects_work_ids_trgm
    ON projects USING GIN (work_ids_text gin_trgm_ops);

COMMIT;
