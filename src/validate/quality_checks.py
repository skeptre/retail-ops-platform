import logging
from sqlalchemy import text

logger = logging.getLogger(__name__)

CHECKS = [
    {
        'name': 'no_negative_quantities',
        'sql': 'SELECT COUNT(*) FROM silver.transactions WHERE quantity <= 0',
        'expected_value': 0,
        'severity': 'error'
    },
    {
        'name': 'no_future_transactions',
        'sql': "SELECT COUNT(*) FROM silver.transactions WHERE transaction_ts > NOW()",
        'expected_value': 0,
        'severity': 'error'
    },
    {
        'name': 'quarantine_rate_under_10pct',
        'sql': """
            SELECT ROUND(
                COUNT(*) FILTER (WHERE _is_quarantined) * 100.0 / NULLIF(COUNT(*), 0), 2
            )
            FROM bronze.raw_transactions
        """,
        'max_value': 10.0,
        'severity': 'error'
    },
    {
        'name': 'silver_transactions_not_empty',
        'sql': 'SELECT COUNT(*) FROM silver.transactions',
        'min_value': 1,
        'severity': 'error'
    },
    {
        'name': 'gold_daily_sales_not_empty',
        'sql': 'SELECT COUNT(*) FROM gold.daily_store_sales',
        'min_value': 1,
        'severity': 'warning'
    },
    {
        'name': 'all_stores_have_sales',
        'sql': """
            SELECT COUNT(*) FROM silver.stores s
            LEFT JOIN silver.transactions t ON s.store_id = t.store_id
            WHERE t.store_id IS NULL
        """,
        'expected_value': 0,
        'severity': 'warning'
    }
]


def run_checks(engine) -> None:
    logger.info(f'Running {len(CHECKS)} quality checks')
    failures = []

    for check in CHECKS:
        with engine.connect() as conn:
            result = conn.execute(text(check['sql'])).scalar()

        passed = True

        if 'expected_value' in check and result != check['expected_value']:
            passed = False
        if 'max_value' in check and float(result or 0) > check['max_value']:
            passed = False
        if 'min_value' in check and (result is None or result < check['min_value']):
            passed = False

        if passed:
            logger.info(f'PASS | {check["name"]} | result: {result}')
        else:
            msg = f'FAIL [{check["severity"].upper()}] | {check["name"]} | result: {result}'
            logger.warning(msg)
            if check['severity'] == 'error':
                failures.append(msg)

    if failures:
        raise ValueError(f'Quality checks failed:\n' + '\n'.join(failures))

    logger.info('All quality checks passed')