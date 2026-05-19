from fastapi import FastAPI
from src.api.routers import health as health, sales, inventory, pipeline

app = FastAPI(
    title='Retail Ops Intelligence API',
    description='Analytics API for the Retail Operations Platform',
    version='1.0.0'
)

app.include_router(health.router, tags=['Health'])
app.include_router(sales.router, prefix='/api/v1/sales', tags=['Sales'])
app.include_router(inventory.router, prefix='/api/v1/inventory', tags=['Inventory'])
app.include_router(pipeline.router, prefix='/api/v1/pipeline', tags=['Pipeline'])