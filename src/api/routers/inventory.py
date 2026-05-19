from fastapi import APIRouter
from sqlalchemy import text
from src.db.connection import get_engine

router = APIRouter()

@router.get('/alerts')
def inventory_alerts():
    sql = """
        SELECT
            i.store_id,
            s.store_name,
            i.product_id,
            i.stock_level,
            i.reorder_point,
            i.reorder_point - i.stock_level as units_needed
        FROM silver.inventory i
        JOIN silver.stores s ON i.store_id = s.store_id
        WHERE i.is_below_reorder = TRUE
        ORDER BY i.store_id, i.product_id
    """
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return [dict(row._mapping) for row in rows]


@router.get('/health-snapshot')
def inventory_health():
    sql = """
        SELECT *
        FROM gold.inventory_health
        WHERE snapshot_date = (SELECT MAX(snapshot_date) FROM gold.inventory_health)
        ORDER BY reorder_rate DESC
    """
    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(sql)).fetchall()
    return [dict(row._mapping) for row in rows]