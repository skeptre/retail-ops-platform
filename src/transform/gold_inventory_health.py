import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

SQL = """
INSERT INTO gold.inventory_health (
    snapshot_date, store_id,
    products_below_reorder, total_products, reorder_rate
)
SELECT
    CURRENT_DATE,
    store_id,
    COUNT(*) FILTER (WHERE is_below_reorder = TRUE),
    COUNT(*),
    ROUND(COUNT(*) FILTER (WHERE is_below_reorder = TRUE) * 100.0 / COUNT(*), 2)
FROM silver.inventory
GROUP BY store_id
ON CONFLICT (snapshot_date, store_id) DO UPDATE
    SET products_below_reorder = EXCLUDED.products_below_reorder,
        total_products         = EXCLUDED.total_products,
        reorder_rate           = EXCLUDED.reorder_rate,
        _refreshed_at          = NOW();
"""

def run(engine) -> int:
    with engine.begin() as conn:
        result = conn.execute(text(SQL))
        logger.info(f'Gold inventory health: {result.rowcount} rows upserted')
    return result.rowcount