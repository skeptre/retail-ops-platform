import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

SQL = """
INSERT INTO silver.inventory (
    store_id, product_id, stock_level,
    reorder_point, is_below_reorder,
    last_restocked, supplier_id
)
SELECT
    store_id::INT,
    product_id::INT,
    stock_level::INT,
    reorder_point::INT,
    stock_level::INT < reorder_point::INT,
    last_restocked::DATE,
    supplier_id::INT
FROM bronze.raw_inventory
WHERE store_id IS NOT NULL
  AND product_id IS NOT NULL
  AND stock_level ~ '^[0-9]+$'
  AND reorder_point ~ '^[0-9]+$'
ON CONFLICT (store_id, product_id) DO UPDATE
    SET stock_level      = EXCLUDED.stock_level,
        reorder_point    = EXCLUDED.reorder_point,
        is_below_reorder = EXCLUDED.is_below_reorder,
        last_restocked   = EXCLUDED.last_restocked,
        _transformed_at  = NOW();
"""

def run(engine) -> int:
    with engine.begin() as conn:
        result = conn.execute(text(SQL))
        logger.info(f'Silver inventory: {result.rowcount} rows upserted')
    return result.rowcount