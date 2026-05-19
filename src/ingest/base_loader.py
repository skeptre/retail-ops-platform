import time
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

logger = logging.getLogger(__name__)


class BaseLoader:
    def __init__(self, engine, quarantine_dir: Path):
        self.engine = engine
        self.quarantine_dir = Path(quarantine_dir)
        self.quarantine_dir.mkdir(parents=True, exist_ok=True)

    def load_with_retry(self, df: pd.DataFrame, table: str, schema: str = 'bronze', max_retries: int = 3) -> int:
        for attempt in range(max_retries):
            try:
                df.to_sql(
                    table,
                    self.engine,
                    schema=schema,
                    if_exists='append',
                    index=False
                )
                logger.info(f'Loaded {len(df)} rows to {schema}.{table}')
                return len(df)
            except Exception as e:
                wait = 2 ** attempt
                logger.warning(f'Attempt {attempt + 1} failed: {e}. Retrying in {wait}s')
                if attempt == max_retries - 1:
                    self._quarantine(df, table, str(e))
                    raise
                time.sleep(wait)
        return 0

    def _quarantine(self, df: pd.DataFrame, table: str, reason: str) -> None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f'{table}_{timestamp}.csv'
        path = self.quarantine_dir / fname
        df.assign(_quarantine_reason=reason).to_csv(path, index=False)
        logger.error(f'Quarantined {len(df)} rows → {path}')