import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

SQL = """
INSERT INTO silver.stores (
    store_id, store_name, city, region, store_type, opened_date
)
SELECT
    store_id::INT,
    store_name,
    city,
    region,
    store_type,
    opened_date::DATE
FROM bronze.raw_stores
WHERE store_id IS NOT NULL
  AND store_name IS NOT NULL
ON CONFLICT (store_id) DO UPDATE
    SET store_name      = EXCLUDED.store_name,
        city            = EXCLUDED.city,
        region          = EXCLUDED.region,
        store_type      = EXCLUDED.store_type,
        opened_date     = EXCLUDED.opened_date,
        _transformed_at = NOW();
"""

def run(engine) -> int:
    with engine.begin() as conn:
        result = conn.execute(text(SQL))
        logger.info(f'Silver stores: {result.rowcount} rows upserted')
    return result.rowcount