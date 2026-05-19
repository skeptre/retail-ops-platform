# One-command bootstrap for Windows
Write-Host "Starting infrastructure..."
Set-Location docker
docker compose up -d
Set-Location ..

Write-Host "Waiting for PostgreSQL to be ready..."
Start-Sleep -Seconds 10

Write-Host "Generating mock data..."
python -m src.generate.stores
python -m src.generate.inventory
python -m src.generate.transactions

Write-Host "Running pipeline..."
python -m src.orchestrate.pipeline_flow

Write-Host "Done. API available at http://localhost:8000/docs"
Write-Host "Start the API with: uvicorn src.api.main:app --reload"