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
    city                TEXT,
    region              TEXT,
    store_type          TEXT,
    opened_date         TEXT
);

-- ============================================================
-- SILVER LAYER
-- ============================================================

CREATE TABLE IF NOT EXISTS silver.stores (
    store_id        INT PRIMARY KEY,
    store_name      TEXT NOT NULL,
    city            TEXT,
    region          TEXT,
    store_type      TEXT,
    opened_date     DATE,
    _transformed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.transactions (
    transaction_id  UUID PRIMARY KEY,
    store_id        INT NOT NULL,
    product_id      INT NOT NULL,
    quantity        INT NOT NULL,
    unit_price      NUMERIC(10,2) NOT NULL,
    total_amount    NUMERIC(10,2),
    transaction_ts  TIMESTAMPTZ NOT NULL,
    payment_method  TEXT,
    cashier_id      INT,
    _bronze_id      BIGINT REFERENCES bronze.raw_transactions(_id),
    _transformed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS silver.inventory (
    store_id         INT NOT NULL,
    product_id       INT NOT NULL,
    stock_level      INT NOT NULL,
    reorder_point    INT NOT NULL,
    is_below_reorder BOOLEAN,
    last_restocked   DATE,
    supplier_id      INT,
    _transformed_at  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (store_id, product_id)
);

-- ============================================================
-- GOLD LAYER
-- ============================================================

CREATE TABLE IF NOT EXISTS gold.daily_store_sales (
    report_date       DATE NOT NULL,
    store_id          INT NOT NULL,
    store_name        TEXT,
    total_revenue     NUMERIC(12,2),
    transaction_count INT,
    avg_basket_size   NUMERIC(10,2),
    _refreshed_at     TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (report_date, store_id)
);

CREATE TABLE IF NOT EXISTS gold.inventory_health (
    snapshot_date          DATE NOT NULL,
    store_id               INT NOT NULL,
    products_below_reorder INT,
    total_products         INT,
    reorder_rate           NUMERIC(5,2),
    _refreshed_at          TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (snapshot_date, store_id)
);