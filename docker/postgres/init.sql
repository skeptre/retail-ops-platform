CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- ============================================================
-- BRONZE LAYER
-- ============================================================

CREATE TABLE IF NOT EXISTS bronze.pipeline_runs (
    run_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flow_name           TEXT,
    started_at          TIMESTAMPTZ DEFAULT NOW(),
    finished_at         TIMESTAMPTZ,
    status              TEXT,
    records_loaded      INT,
    records_quarantined INT DEFAULT 0,
    error_message       TEXT
);

CREATE TABLE IF NOT EXISTS bronze.raw_transactions (
    _id                 BIGSERIAL PRIMARY KEY,
    _ingested_at        TIMESTAMPTZ DEFAULT NOW(),
    _source_file        TEXT,
    _is_quarantined     BOOLEAN DEFAULT FALSE,
    _quarantine_reason  TEXT,
    transaction_id      TEXT,
    store_id            TEXT,
    product_id          TEXT,
    quantity            TEXT,
    unit_price          TEXT,
    transaction_ts      TEXT,
    payment_method      TEXT,
    cashier_id          TEXT
);

CREATE TABLE IF NOT EXISTS bronze.raw_inventory (
    _id                 BIGSERIAL PRIMARY KEY,
    _ingested_at        TIMESTAMPTZ DEFAULT NOW(),
    _source_file        TEXT,
    _is_quarantined     BOOLEAN DEFAULT FALSE,
    _quarantine_reason  TEXT,
    store_id            TEXT,
    product_id          TEXT,
    stock_level         TEXT,
    reorder_point       TEXT,
    last_restocked      TEXT,
    supplier_id         TEXT
);

CREATE TABLE IF NOT EXISTS bronze.raw_stores (
    _id                 BIGSERIAL PRIMARY KEY,
    _ingested_at        TIMESTAMPTZ DEFAULT NOW(),
    _source_file        TEXT,
    store_id            TEXT,
    store_name          TEXT,
    c