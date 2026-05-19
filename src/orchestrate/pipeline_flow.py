from prefect.cache_policies import NO_CACHE
import logging
import uuid
import os
from datetime import datetime, timezone
from pathlib import Path

from prefect import flow, task, get_run_logger
from sqlalchemy import text
from dotenv import load_dotenv

from src.db.connection import get_engine
from src.ingest.load_stores import StoreLoader
from src.ingest.load_inventory import InventoryLoader
from src.ingest.load_transactions import TransactionLoader
from src.transform import silver_stores, silver_inventory, silver_transactions
from src.transform import gold_daily_sales, gold_inventory_health
from src.validate.quality_checks import run_checks

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)


@task(retries=2, retry_delay_seconds=10, name='ingest-stores', cache_policy=NO_CACHE)
def task_ingest_stores(engine, quarantine_dir):
    logger = get_run_logger()
    count = StoreLoader(engine, Path(quarantine_dir)).load(Path('data/raw/stores/stores.csv'))
    logger.info(f'Ingested {count} store rows')
    return count


@task(retries=2, retry_delay_seconds=10, name='ingest-inventory', cache_policy=NO_CACHE)
def task_ingest_inventory(engine, quarantine_dir):
    logger = get_run_logger()
    count = InventoryLoader(engine, Path(quarantine_dir)).load(Path('data/raw/inventory/inventory.csv'))
    logger.info(f'Ingested {count} inventory rows')
    return count


@task(retries=2, retry_delay_seconds=10, name='ingest-transactions', cache_policy=NO_CACHE)
def task_ingest_transactions(engine, quarantine_dir):
    logger = get_run_logger()
    count = TransactionLoader(engine, Path(quarantine_dir)).load(Path('data/raw/transactions/transactions.csv'))
    logger.info(f'Ingested {count} transaction rows')
    return count


@task(name='transform-silver', cache_policy=NO_CACHE)
def task_transform_silver(engine):
    logger = get_run_logger()
    silver_stores.run(engine)
    silver_inventory.run(engine)
    silver_transactions.run(engine)
    logger.info('Silver transformations complete')


@task(name='build-gold', cache_policy=NO_CACHE)
def task_build_gold(engine):
    logger = get_run_logger()
    gold_daily_sales.run(engine)
    gold_inventory_health.run(engine)
    logger.info('Gold tables complete')

@task(name='validate', cache_policy=NO_CACHE)
def task_validate(engine):
    logger = get_run_logger()
    run_checks(engine)
    logger.info('Validation passed')


@flow(name='retail-ops-pipeline')
def run_pipeline():
    engine = get_engine()
    run_id = str(uuid.uuid4())
    quarantine_dir = os.getenv('QUARANTINE_DIR', 'data/quarantine')

    # Log run start
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO bronze.pipeline_runs (run_id, flow_name, status)
            VALUES (:run_id, 'retail-ops-pipeline', 'running')
        """), {'run_id': run_id})

    status = 'failed'
    try:
        # Ingest
        task_ingest_stores(engine, quarantine_dir)
        task_ingest_inventory(engine, quarantine_dir)
        task_ingest_transactions(engine, quarantine_dir)

        # Transform
        task_transform_silver(engine)
        task_build_gold(engine)

        # Validate
        task_validate(engine)

        status = 'success'

    except Exception as e:
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE bronze.pipeline_runs
                SET status = 'failed',
                    finished_at = NOW(),
                    error_message = :err
                WHERE run_id = :run_id
            """), {'err': str(e), 'run_id': run_id})
        raise

    finally:
        with engine.begin() as conn:
            conn.execute(text("""
                UPDATE bronze.pipeline_runs
                SET status = :status,
                    finished_at = NOW()
                WHERE run_id = :run_id
            """), {'status': status, 'run_id': run_id})


if __name__ == '__main__':
    run_pipeline()