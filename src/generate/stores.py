import pandas as pd
from pathlib import Path
from datetime import date

STORES = [
    (1, 'Manchester Flagship', 'Manchester', 'North West', 'flagship'),
    (2, 'London Central',      'London',     'London',     'flagship'),
    (3, 'Edinburgh Warehouse', 'Edinburgh',  'Scotland',   'warehouse'),
    (4, 'Birmingham Outlet',   'Birmingham', 'Midlands',   'outlet'),
    (5, 'Bristol Flagship',    'Bristol',    'South West', 'flagship'),
    (6, 'Leeds Warehouse',     'Leeds',      'Yorkshire',  'warehouse'),
    (7, 'Cardiff Outlet',      'Cardiff',    'Wales',      'outlet'),
    (8, 'Liverpool Flagship',  'Liverpool',  'North West', 'flagship'),
    (9, 'Glasgow Warehouse',   'Glasgow',    'Scotland',   'warehouse'),
    (10,'Newcastle Outlet',    'Newcastle',  'North East', 'outlet'),
]

def generate_stores(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(STORES, columns=[
        'store_id', 'store_name', 'city', 'region', 'store_type'
    ])
    df['opened_date'] = pd.date_range(
        start='2018-01-01', periods=len(df), freq='180D'
    ).strftime('%Y-%m-%d')
    output_path = output_dir / 'stores.csv'
    df.to_csv(output_path, index=False)
    print(f'Generated {len(df)} stores → {output_path}')
    return output_path

if __name__ == '__main__':
    generate_stores(Path('data/raw/stores'))