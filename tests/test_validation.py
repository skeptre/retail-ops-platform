import pytest
from unittest.mock import MagicMock, patch


def make_mock_engine(scalar_value):
    """Helper to create a mock engine returning a specific scalar value."""
    mock_conn = MagicMock()
    mock_conn.execute.return_value.scalar.return_value = scalar_value
    mock_conn.__enter__ = lambda s: mock_conn
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    return mock_engine


def run_single_check(check: dict, engine) -> bool:
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text(check['sql'])).scalar()
    if 'expected_value' in check and result != check['expected_value']:
        return False
    if 'max_value' in check and float(result or 0) > check['max_value']:
        return False
    if 'min_value' in check and (result is None or result < check['min_value']):
        return False
    return True


def test_quarantine_rate_passes_under_threshold():
    engine = make_mock_engine(5.0)
    check = {'sql': 'SELECT 1', 'max_value': 10.0, 'severity': 'error'}
    assert run_single_check(check, engine) is True


def test_quarantine_rate_fails_over_threshold():
    engine = make_mock_engine(15.0)
    check = {'sql': 'SELECT 1', 'max_value': 10.0, 'severity': 'error'}
    assert run_single_check(check, engine) is False


def test_expected_value_check_passes():
    engine = make_mock_engine(0)
    check = {'sql': 'SELECT 1', 'expected_value': 0, 'severity': 'error'}
    assert run_single_check(check, engine) is True


def test_expected_value_check_fails():
    engine = make_mock_engine(5)
    check = {'sql': 'SELECT 1', 'expected_value': 0, 'severity': 'error'}
    assert run_single_check(check, engine) is False


def test_min_value_check_passes():
    engine = make_mock_engine(100)
    check = {'sql': 'SELECT 1', 'min_value': 1, 'severity': 'error'}
    assert run_single_check(check, engine) is True


def test_min_value_check_fails_on_empty():
    engine = make_mock_engine(0)
    check = {'sql': 'SELECT 1', 'min_value': 1, 'severity': 'error'}
    assert run_single_check(check, engine) is False
