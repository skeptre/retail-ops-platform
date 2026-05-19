from fastapi import APIRouter
from sqlalchemy import text
from src.db.connection import get_engine
from typing import Optional
from datetime import date

router = APIRouter()

@router.get('/daily')
def daily_sales(
    store_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    sql = 'SELECT * FROM gold.daily_store_sales WHERE 1=1'
    params = {}
    if store_id:
        sql += ' AND store_id = :store_id'
        params['store_id'] = store_id
    if start_date:
        sql += ' AND report_date >= :start_date'
        params['start_date'] = start_date
    if end_date:
        sql += ' AND report_date <= :end_date'
        params['end_date'] = end_date
    sql += ' ORDER BY report_date DESC LIMIT 100'

    engine = get_engine()
    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).fetchall()
    return [dict(row._mapping) for row in rows]


@router.get('/summary')
def sales_summary(period: str = '7d'):
    days = {'7d': 7, '30d': 30, '90d': 90}.get(period, 7)
    sql = f"""
        SELECT
            COUNT(*) as transaction_count,
            ROUND(SUM(total_revenue), 2) as total_revenue,
            ROUND(AVG(avg_basket_size), 2) as avg_basket_size,
            MAX(store_name) FILTER (WHERE total_revenue = (
                SELECT MAX(total_revenue) FROM gold.daily_store_sales
                WHERE report_date >= CURRENT_DATE - INTERVAL '{days} days'
            )) as top_store
        FROM gold.daily_store_sales
        WHERE report_date >= CURRENT_DATE - INTERVAL '{days} days'
    """
    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(text(sql)).fetchone()
    return dict(row._mapping) if row is not None else {}