import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

SQL = """
INSERT INTO gold.daily_store_sales (
    report_date, store_id, store_name,
    total_revenue, transaction_count, avg_basket_size
)
SELECT
    DATE_TRUNC('day', t.transaction_ts)::DATE AS report_date,
    t.store_id,
    s.store_name,
    ROUND(SUM(t.total_amount), 2),
    COUNT(*),
    ROUND(AVG(t.total_amount), 2)
FROM silver.transactions t
JOIN silver.stores s ON t.store_id = s.store_id
GROUP BY 1, 2, 3
ON CONFLICT (report_date, store_id) DO UPDATE
    SET total_revenue     = EXCLUDED.total_revenue,
        transaction_count = EXCLUDED.transaction_count,
        avg_basket_size   = EXCLUDED.avg_basket_size,
        _refreshed_at     = NOW();
"""

def run(engine) -> int:
    with engine.begin() as conn:
        result = conn.execute(text(SQL))
        logger.info(f'Gold daily sales: {result.rowcount} rows upserted')
    return result.rowcount