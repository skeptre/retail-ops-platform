import pytest
import pandas as pd


@pytest.fixture
def sample_raw_transactions():
    return pd.DataFrame({
        'transaction_id': [
            'abc12345-1234-1234-1234-abc123456789',
            'abc12345-1234-1234-1234-abc123456789',  # duplicate
            'def12345-1234-1234-1234-def123456789',
            None,                                     # null
            'ghi12345-1234-1234-1234-ghi123456789',
        ],
        'store_id':       ['1', '1', '2', '3', '1'],
        'product_id':     ['10', '10', '20', '30', '40'],
        'quantity':       ['5', '5', '3', None, '-2'],
        'unit_price':     ['9.99', '9.99', '4.99', '2.99', '14.99'],
        'transaction_ts': [
            '2024-01-15 10:00:00',
            '2024-01-15 10:00:00',
            '2024-01-16 11:00:00',
            '2024-01-17 12:00:00',
            '2099-01-01 00:00:00',   # future date
        ],
        'payment_method': ['card', 'card', 'cash', 'card', 'card'],
        'cashier_id':     ['1', '1', '2', '3', '4'],
    })


@pytest.fixture
def sample_raw_inventory():
    return pd.DataFrame({
        'store_id':      ['1', '1', '2', None],
        'product_id':    ['10', '20', '10', '30'],
        'stock_level':   ['5', '100', 'abc', '20'],
        'reorder_point': ['10', '50', '15', '25'],
        'last_restocked': ['2024-01-01', '2024-01-05', '2024-01-10', '2024-01-15'],
        'supplier_id':   ['1', '2', '3', '4'],
    })
