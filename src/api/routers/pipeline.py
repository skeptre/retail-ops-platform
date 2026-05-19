from fastapi import APIRouter
from sqlalchemy import text
from src.db.connection import get_engine

router = APIRouter()

@router.get('/runs')
def pipeline_runs(limit: int = 10):
    sql = """
        SELECT
            run_id,
            flow_name,
            status,
            started_at,
            finished_at,
            records_loaded,
            records_quarantined,
            error_message
        FROM bronze.pipeline_runs
        ORDER BY started_at DESC
        LIMIT :limit
    """
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(sql), {'limit': limit}).fetchall()
    return [dict(row._mapping) for row in rows]