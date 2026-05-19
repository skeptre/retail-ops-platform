# Retail Ops Platform — Windows Bootstrap Script
# Starts infrastructure, clears old data, generates fresh data, runs pipeline

param(
    [switch]$SkipDocker
)

$ErrorActionPreference = "Stop"

# Check .env exists
if (-not (Test-Path ".env")) {
    Write-Error ".env file not found. Copy .env.example to .env and fill in your values."
    exit 1
}

# Start Docker
if (-not $SkipDocker) {
    Write-Host "Starting infrastructure..." -ForegroundColor Cyan
    Set-Location docker
    docker compose up -d
    Set-Location ..
    Write-Host "Waiting for PostgreSQL to be ready..."
    Start-Sleep -Seconds 15
}

# Truncate all tables for a clean run
Write-Host "Clearing existing data..." -ForegroundColor Cyan
python -c "
from dotenv import load_dotenv
load_dotenv()
from src.db.connection import get_engine
from sqlalchemy import text
engine = get_engine()
with engine.begin() as conn:
    conn.execute(text('TRUNCATE TABLE silver.transactions CASCADE'))
    conn.execute(text('TRUNCATE TABLE silver.inventory'))
    conn.execute(text('TRUNCATE TABLE silver.stores'))
    conn.execute(text('TRUNCATE TABLE bronze.raw_transactions CASCADE'))
    conn.execute(text('TRUNCATE TABLE bronze.raw_inventory CASCADE'))
    conn.execute(text('TRUNCATE TABLE bronze.raw_stores CASCADE'))
    conn.execute(text('TRUNCATE TABLE gold.daily_store_sales'))
    conn.execute(text('TRUNCATE TABLE gold.inventory_health'))
    conn.execute(text('TRUNCATE TABLE bronze.pipeline_runs'))
print('Tables cleared')
"

# Generate mock data
Write-Host "Generating mock data..." -ForegroundColor Cyan
python -m src.generate.stores
python -m src.generate.inventory
python -m src.generate.transactions

# Run pipeline
Write-Host "Running pipeline..." -ForegroundColor Cyan
python -m src.orchestrate.pipeline_flow

Write-Host ""
Write-Host "Done." -ForegroundColor Green
Write-Host "Start the API with: uvicorn src.api.main:app --reload"
Write-Host "Then open: http://localhost:8000/docs"