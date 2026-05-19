import pandas as pd
import pytest
from datetime import datetime


def apply_transaction_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Mirror of the silver transformation filter logic."""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    df = df.copy()
    df = df[df['transaction_id'].notna()]
    df = df[df['transaction_id'].str.match(uuid_pattern, na=False)]
    df = df[df['quantity'].notna()]
    df = df[df['quantity'].str.match(r'^[0-9]+$', na=False)]
    df = df[df['quantity'].astype(int) > 0]
    df = df[df['unit_price'].str.match(r'^[0-9]+(\.[0-9]+)?$', na=False)]
    df = df[df['unit_price'].astype(float) >= 0]
    df = df[pd.to_datetime(df['transaction_ts']) <= datetime.now()]
    df = df.drop_duplicates(subset=['transaction_id'], keep='first')
    return df


def apply_inventory_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Mirror of the silver inventory filter logic."""
    df = df.copy()
    df = df[df['store_id'].notna()]
    df = df[df['product_id'].notna()]
    df = df[df['stock_level'].str.match(r'^[0-9]+$', na=False)]
    df = df[df['reorder_point'].str.match(r'^[0-9]+$', na=False)]
    return df


def test_filters_null_transaction_id(sample_raw_transactions):
    result = apply_transaction_filters(sample_raw_transactions)
    assert result['transaction_id'].notna().all()


def test_filters_negative_quantity(sample_raw_transactions):
    result = apply_transaction_filters(sample_raw_transactions)
    assert (result['quantity'].astype(int) > 0).all()


def test_filters_future_timestamps(sample_raw_transactions):
    result = apply_transaction_filters(sample_raw_transactions)
    assert (pd.to_datetime(result['transaction_ts']) <= datetime.now()).all()


def test_filters_duplicate_transaction_ids(sample_raw_transactions):
    result = apply_transaction_filters(sample_raw_transactions)
    assert result['transaction_id'].nunique() == len(result)


def test_total_amount_calculated_correctly(sample_raw_transactions):
    result = apply_transaction_filters(sample_raw_transactions)
    result['total_amount'] = result['quantity'].astype(float) * result['unit_price'].astype(float)
    assert (result['total_amount'] > 0).all()


def test_inventory_filters_null_store_id(sample_raw_inventory):
    result = apply_inventory_filters(sample_raw_inventory)
    assert result['store_id'].notna().all()


def test_inventory_filters_non_numeric_stock(sample_raw_inventory):
    result = apply_inventory_filters(sample_raw_inventory)
    assert result['stock_level'].str.match(r'^[0-9]+$').all()


def test_is_below_reorder_calculated_correctly(sample_raw_inventory):
    result = apply_inventory_filters(sample_raw_inventory)
    result['is_below_reorder'] = result['stock_level'].astype(int) < result['reorder_point'].astype(int)
    first_row = result.iloc[0]
    assert first_row['is_below_reorder'] == (int(first_row['stock_level']) < int(first_row['reorder_point']))
