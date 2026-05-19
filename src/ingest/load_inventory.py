import logging
from pathlib import Path
from datetime import datetime

import pandas as pd

from src.ingest.base_loader import BaseLoader

logger = logging.getLogger(__name__)


class InventoryLoader(BaseLoader):
    def load(self, csv_path: Path) -> int:
        logger.info(f'Loading inventory from {csv_path}')
        df = pd.read_csv(csv_path, dtype=str)
        df['_source_file'] = str(csv_path)
        df['_ingested_at'] = datetime.now().isoformat()
        return self.load_with_retry(df, 'raw_inventory')