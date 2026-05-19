from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from src.db.connection import get_engine

router = APIRouter()

@router.get('/health')
def health_check():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            run = conn.execute(text(
                'SELECT status, finished_at FROM bronze.pipeline_runs ORDER BY started_at DESC LIMIT 1'
            )).fetchone()
        return {
            'status': 'healthy',
            'db_connected': True,
            'last_pipeline_run': run.finished_at.isoformat() if run else None,
            'pipeline_status': run.status if run else 'never_run'
        }
    except Exception as e:
        return JSONResponse(status_code=503, content={'status': 'unhealthy', 'error': str(e)})