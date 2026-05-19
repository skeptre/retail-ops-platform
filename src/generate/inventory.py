import pandas as pd
import random
from pathlib import Path
from datetime import datetime, timedelta

STORE_IDS = list(range(1, 11))
PRODUCT_IDS = list(range(1, 201))
SUPPLIER_IDS = list(range(1, 21))

def random_restock_date(days_ago=60):
    return (datetime.now() - timedelta(days=random.randint(1, days_ago))).strftime('%Y-%m-%d')

def generate_inventory(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for store_id in STORE_IDS:
        for product_id in PRODUCT_IDS:
            reorder_point = random.randint(10, 50)

            # Make ~20% of products below reorder point
            if random.random() < 0.20:
                stock_level = random.randint(0, reorder_point - 1)
            else:
                stock_level = random.randint(reorder_point, 200)

            rows.append({
                'store_id':      store_id,
                'product_id':    product_id,
                'stock_level':   stock_level,
                'reorder_point': reorder_point,
                'last_restocked': random_restock_date(),
                'supplier_id':   random.choice(SUPPLIER_IDS),
            })

    df = pd.DataFrame(rows)
    output_path = output_dir / 'inventory.csv'
    df.to_csv(output_path, index=False)
    print(f'Generated {len(df)} inventory records → {output_path}')
    return output_path

if __name__ == '__main__':
    generate_inventory(Path('data/raw/inventory'))