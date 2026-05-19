import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

SQL = """
INSERT INTO silver.transactions (
    transaction_id, store_id, product_id,
    quantity, unit_price, total_amount,
    transaction_ts, payment_method, cashier_id, _bronze_id
)
SELECT
    transaction_id::UUID,
    store_id::INT,
    product_id::INT,
    quantity::INT,
    unit_price::NUMERIC(10,2),
    quantity::INT * unit_price::NUMERIC(10,2),
    transaction_ts::TIMESTAMPTZ,
    payment_method,
    cashier_id::INT,
    _id
FROM bronze.raw_transactions
WHERE transaction_id IS NOT NULL
  AND transaction_id ~ '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
  AND quantity ~ '^[0-9]+$'
  AND quantity::INT > 0
  AND unit_price ~ '^[0-9]+(\\.[0-9]+)?$'
  AND unit_price::NUMERIC >= 0
  AND transaction_ts::TIMESTAMPTZ <= NOW()
ON CONFLICT (transaction_id) DO NOTHING;
"""

QUARANTINE_SQL = """
UPDATE bronze.raw_transactions
SET _is_quarantined = TRUE,
    _quarantine_reason = 'Failed silver transformation checks'
WHERE _id NOT IN (
    SELECT _bronze_id FROM silver.transactions WHERE _bronze_id IS NOT NULL
)
AND _is_quarantined = FALSE;
"""

def run(engine) -> int:
    with engine.begin() as conn:
        result = conn.execute(text(SQL))
        logger.info(f'Silver transactions: {result.rowcount} rows inserted')
        quarantine_result = conn.execute(text(QUARANTINE_SQL))
        logger.info(f'Quarantined {quarantine_result.rowcount} bronze rows')
    return result.rowcount
