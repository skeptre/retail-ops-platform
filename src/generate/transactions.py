import pandas as pd
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_GB')

STORE_IDS = list(range(1, 11))
PRODUCT_IDS = list(range(1, 201))
PAYMENT_METHODS = ['card', 'cash', 'contactless', 'mobile']

def random_date(start_days_ago=90):
    start = datetime.now() - timedelta(days=start_days_ago)
    return start + timedelta(
        seconds=random.randint(0, start_days_ago * 24 * 3600)
    )

def generate_transactions(output_dir: Path, n_rows=50000) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for _ in range(n_rows):
        rows.append({
            'transaction_id': str(uuid.uuid4()),
            'store_id':       random.choice(STORE_IDS),
            'product_id':     random.choice(PRODUCT_IDS),
            'quantity':       random.randint(1, 20),
            'unit_price':     round(random.uniform(0.99, 299.99), 2),
            'transaction_ts': random_date().strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': random.choice(PAYMENT_METHODS),
            'cashier_id':     random.randint(1, 50),
        })

    df = pd.DataFrame(rows)

    # --- Inject dirty data (~3%) ---
    dirty_idx = random.sample(range(n_rows), int(n_rows * 0.03))

    # Null transaction IDs
    for i in dirty_idx[:10]:
        df.at[i, 'transaction_id'] = None

    # Negative quantities
    for i in dirty_idx[10:20]:
        df.at[i, 'quantity'] = -1

    # Negative prices
    for i in dirty_idx[20:30]:
        df.at[i, 'unit_price'] = -9.99

    # Future timestamps
    for i in dirty_idx[30:40]:
        df.at[i, 'transaction_ts'] = '2099-01-01 00:00:00'

    # Duplicate transaction IDs
    for i in dirty_idx[40:50]:
        df.at[i, 'transaction_id'] = df.at[0, 'transaction_id']

    output_path = output_dir / 'transactions.csv'
    df.to_csv(output_path, index=False)
    print(f'Generated {len(df)} transactions → {output_path}')
    return output_path

if __name__ == '__main__':
    generate_transactions(Path('data/raw/transactions'))