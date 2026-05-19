CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS bronze.pipeline_runs (
  run_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  flow_name TEXT,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  status TEXT,
  records_loaded INT,
  records_quarantined INT DEFAULT 0,
  error_message TEXT
);

-- (Add all other CREATE TABLE statements from the schema plan here)