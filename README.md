# Retail & Operations Intelligence Platform

[![CI](https://github.com/skeptre/retail-ops-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/skeptre/retail-ops-platform/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)](https://postgresql.org)
[![Prefect](https://img.shields.io/badge/Prefect-3.x-blue)](https://prefect.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-green)](https://fastapi.tiangolo.com)
[![Tests](https://img.shields.io/badge/Tests-20%20passing-brightgreen)](https://github.com/skeptre/retail-ops-platform)

A production-patterned ELT data platform for a multi-location retail business.
Demonstrates the full data engineering lifecycle: ingestion, transformation,
quality validation, orchestration, and analytics serving.

---

## Architecture

```mermaid
flowchart TD
    CSV1[/"POS Transactions CSV"//]
    CSV2[/"Inventory CSV"//]
    CSV3[/"Stores CSV"//]

    subgraph INGEST ["INGEST s1"]
        L1[Transaction Loader]
        L2[Inventory Loader]
        L3[Store Loader]
    end

    subgraph BRONZE ["BRONZE s2"]
        B1[(raw_transactions)]
        B2[(raw_inventory)]
        B3[(raw_stores)]
        B4[(pipeline_runs)]
        BQ[(quarantine)]
    end

    subgraph SILVER ["SILVER s3"]
        S1[(transactions)]
        S2[(inventory)]
        S3[(stores)]
    end

    subgraph GOLD ["GOLD s4"]
        G1[(daily_store_sales)]
        G2[(inventory_health)]
    end

    subgraph VALIDATE ["VALIDATE s5"]
        V1[s29]
    end

    subgraph API ["API s6"]
        A1[/GET /health//]
        A2[/GET /sales/daily//]
        A3[/GET /sales/summary//]
        A4[/GET /inventory/alerts//]
        A5[/GET /pipeline/runs//]
    end

    PREFECT["Prefect Orchestrator"]

    CSV1 --> L1
    CSV2 --> L2
    CSV3 --> L3

    L1 -->|retry + quarantine| B1
    L2 -->|retry + quarantine| B2
    L3 -->|retry + quarantine| B3
    L1 -->|failed batches| BQ

    B1 -->|DISTINCT ON + type cast| S1
    B2 -->|DISTINCT ON + type cast| S2
    B3 -->|upsert| S3

    S1 -->|GROUP BY date + store| G1
    S2 -->|reorder rate| G2

    G1 --> V1
    G2 --> V1
    S1 --> V1

    V1 -->|pass| B4
    V1 -->|fail abort| B4

    G1 --> A2
    G1 --> A3
    G2 --> A4
    B4 --> A1
    B4 --> A5

    PREFECT -->|orchestrates| INGEST
    PREFECT -->|orchestrates| SILVER
    PREFECT -->|orchestrates| GOLD
    PREFECT -->|orchestrates| VALIDATE

    classDef csv fill:#f8fafc,stroke:#64748b,stroke-width:1.5px,color:#0f172a
    classDef ingest fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e3a8a
    classDef bronze fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f
    classDef silver fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#0c4a6e
    classDef gold fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d
    classDef validate fill:#f3e8ff,stroke:#9333ea,stroke-width:2px,color:#581c87
    classDef api fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#3b0764
    classDef orchestrator fill:#111827,stroke:#6366f1,stroke-width:2px,color:#ffffff
    classDef danger fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d

    class CSV1,CSV2,CSV3 csv
    class L1,L2,L3 ingest
    class B1,B2,B3,B4 bronze
    class BQ danger
    class S1,S2,S3 silver
    class G1,G2 gold
    class V1 validate
    class A1,A2,A3,A4,A5 api
    class PREFECT orchestrator

    style INGEST fill:#eff6ff,stroke:#60a5fa,stroke-width:1px,color:#1e3a8a
    style BRONZE fill:#fffbeb,stroke:#f59e0b,stroke-width:1px,color:#78350f
    style SILVER fill:#f0f9ff,stroke:#38bdf8,stroke-width:1px,color:#0c4a6e
    style GOLD fill:#f0fdf4,stroke:#4ade80,stroke-width:1px,color:#14532d
    style VALIDATE fill:#faf5ff,stroke:#c084fc,stroke-width:1px,color:#581c87
    style API fill:#f5f3ff,stroke:#a78bfa,stroke-width:1px,color:#3b0764
```

**Orchestration:** Prefect flow chains all stages with retries and run metadata logging.  
**Validation:** Quality checks run after transformation — error-severity failures abort the pipeline.  
**Containerisation:** Docker Compose runs PostgreSQL and pgAdmin locally.

---

## Quick Start

**Prerequisites:** Docker Desktop, Python 3.11+, Git

```bash
# 1. Clone
git clone https://github.com/skeptre/retail-ops-platform
cd retail-ops-platform

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env        # Windows
cp .env.example .env          # Mac/Linux
# Edit .env with your values

# 5. Start infrastructure
cd docker && docker compose up -d && cd ..

# 6. Generate mock data
python -m src.generate.stores
python -m src.generate.inventory
python -m src.generate.transactions

# 7. Run the pipeline
python -m src.orchestrate.pipeline_flow

# 8. Start the API
uvicorn src.api.main:app --reload
# Open: http://localhost:8000/docs
```

---

## Design Decisions

### ELT over ETL

Data is loaded into PostgreSQL in raw TEXT format first (bronze layer), then
transformed in-database using SQL. This means raw data is always preserved and
transformations are replayable without re-ingesting. If transformation logic
changes, you re-run the SQL against the same bronze data. ETL would transform
before loading — simpler, but you lose the audit trail.

### Why PostgreSQL over a Data Warehouse

For a portfolio MVP, PostgreSQL demonstrates the same SQL patterns used in
BigQuery, Redshift, and Snowflake at no cost. The medallion schema, upsert
patterns, and quality checks transfer directly to any cloud warehouse. At scale,
the upgrade path is: partition bronze tables by date, move raw files to S3/GCS,
replace PostgreSQL with a columnar warehouse, and add dbt for transformations.

### Medallion Architecture (Bronze / Silver / Gold)

- **Bronze** — raw, append-only, all columns TEXT. Load never fails due to type mismatch.
- **Silver** — typed, validated, deduplicated. One clean record per business entity.
- **Gold** — pre-aggregated for fast API queries. Rebuilt on each pipeline run.

### Idempotency

Every transformation uses `ON CONFLICT DO NOTHING` or `ON CONFLICT DO UPDATE`.
Re-running the pipeline any number of times produces the same result without
duplicating data. This is non-negotiable for scheduled batch pipelines.

### Quarantine Pattern

Records that fail silver transformation checks are flagged with
`_is_quarantined = TRUE` and a reason in `bronze.raw_transactions`. Nothing is
silently dropped. Failed records are recoverable — if transformation logic is
fixed, you can re-process quarantined rows without re-ingesting from source.

### Retry Logic

The `BaseLoader` class retries failed loads up to 3 times with exponential
backoff (1s, 2s, 4s). This handles transient database connectivity issues
without crashing the pipeline. After all retries fail, the batch is written
to `data/quarantine/` as a CSV for manual inspection.

### Pipeline Run Metadata

Every pipeline run writes a record to `bronze.pipeline_runs` with start time,
finish time, status, and any error message. This makes the platform observable
— you can see the full run history via the `/api/v1/pipeline/runs` endpoint
without digging through logs.

### Gold Layer Caching

Gold tables are materialised tables, not views. The API queries gold directly
so responses are fast even with millions of rows in silver. A view would
re-aggregate on every API request.

---

## Trade-offs and Known Limitations

| Limitation | Impact | Upgrade Path |
| --- | --- | --- |
| Batch (daily) not streaming | Data is up to 24h stale | Add Kafka/Kinesis for real-time ingestion |
| Full refresh on gold | Slow at very large scale | Incremental refresh with watermark column |
| Batch-level quarantine | All rows in a failed batch quarantined together | Row-level quarantine with pre-validation |
| No API authentication | Endpoints are open | Add OAuth2/API key middleware |
| PostgreSQL not columnar | Slow analytics at 100M+ rows | Migrate to BigQuery/Redshift/Snowflake |
| Cast safety in SQL | Bad types can error before regex guard runs | Pre-filter with CTE before casting |

---

## Data Quality Checks

| Check | Type | Threshold |
| --- | --- | --- |
| No negative quantities in silver | Error | 0 |
| No future-dated transactions | Error | 0 |
| Quarantine rate under 10% | Error | <10% |
| Silver transactions not empty | Error | ≥1 row |
| Gold daily sales populated | Warning | ≥1 row |
| All stores have at least one sale | Warning | 0 orphans |

Error-severity failures abort the pipeline and mark the run as `failed`.
Warning-severity failures log but allow the run to complete.

---

## API Reference

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Platform health and last pipeline run status |
| GET | `/api/v1/sales/daily` | Daily sales by store with optional filters |
| GET | `/api/v1/sales/summary` | Revenue summary for 7d, 30d, or 90d period |
| GET | `/api/v1/inventory/alerts` | Products currently below reorder point |
| GET | `/api/v1/inventory/health-snapshot` | Reorder rate per store |
| GET | `/api/v1/pipeline/runs` | Recent pipeline run history |

Interactive docs: `http://localhost:8000/docs`

---

## Project Structure

```text
retail-ops-platform/
├── docker/                  # Docker Compose and PostgreSQL init
├── src/
│   ├── generate/            # Mock data generators
│   ├── ingest/              # Bronze layer loaders with retry/quarantine
│   ├── transform/           # Silver and gold SQL transformations
│   ├── validate/            # Data quality checks
│   ├── orchestrate/         # Prefect pipeline flow
│   ├── api/                 # FastAPI app and routers
│   └── db/                  # Database connection
├── tests/                   # Pytest suite (20 tests)
├── data/
│   ├── raw/                 # Generated CSV source files
│   └── quarantine/          # Failed records
└── docs/                    # Architecture diagrams and screenshots
```

---

## Testing

```bash
# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ --cov=src --cov-report=term-missing
```

**Coverage targets:** >80% on `src/transform/` and `src/validate/`

---

## Scalability Notes

This platform is intentionally scoped as a batch ELT MVP. Here is how each
component would evolve at production scale:

- **Ingestion** — Replace CSV files with S3/GCS event triggers. Use Spark or
  Beam for parallel ingestion of large files.
- **Storage** — Partition bronze tables by ingestion date. Migrate to a
  columnar warehouse (BigQuery, Redshift, Snowflake) for analytics workloads.
- **Transformations** — Replace raw SQL scripts with dbt for version-controlled,
  tested, documented transformations.
- **Orchestration** — Deploy Prefect with a dedicated server and workers instead
  of the temporary local server. Use cloud-managed orchestration (Cloud Composer,
  MWAA) for production.
- **Validation** — Replace custom quality checks with Great Expectations for
  richer validation rules and HTML reports.
- **API** — Add authentication (OAuth2/API keys), rate limiting, and response
  caching. Deploy behind a load balancer.

---

## Stack

| Component | Technology |
| --- | --- |
| Language | Python 3.11 |
| Database | PostgreSQL 16 |
| Orchestration | Prefect 3.x |
| API | FastAPI + Uvicorn |
| Data processing | Pandas, SQLAlchemy |
| Testing | Pytest |
| Containerisation | Docker + Docker Compose |
| Mock data | Faker |
