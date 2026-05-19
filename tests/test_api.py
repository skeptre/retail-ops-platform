from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.api.main import app

client = TestClient(app)


def make_mock_engine(rows=None, scalar=None):
    mock_conn = MagicMock()
    if scalar is not None:
        mock_conn.execute.return_value.scalar.return_value = scalar
    if rows is not None:
        mock_conn.execute.return_value.fetchone.return_value = rows
        mock_conn.execute.return_value.fetchall.return_value = rows
    mock_conn.__enter__ = lambda s: mock_conn
    mock_conn.__exit__ = MagicMock(return_value=False)
    mock_engine = MagicMock()
    mock_engine.connect.return_value = mock_conn
    return mock_engine


def test_health_returns_200():
    mock_row = MagicMock()
    mock_row.finished_at.isoformat.return_value = '2024-01-15T10:00:00'
    mock_row.status = 'success'
    with patch('src.api.routers.health.get_engine', return_value=make_mock_engine(rows=mock_row)):
        response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'healthy'


def test_health_returns_db_connected_true():
    mock_row = MagicMock()
    mock_row.finished_at.isoformat.return_value = '2024-01-15T10:00:00'
    mock_row.status = 'success'
    with patch('src.api.routers.health.get_engine', return_value=make_mock_engine(rows=mock_row)):
        response = client.get('/health')
    assert response.json()['db_connected'] is True


def test_daily_sales_returns_200():
    with patch('src.api.routers.sales.get_engine', return_value=make_mock_engine(rows=[])):
        response = client.get('/api/v1/sales/daily')
    assert response.status_code == 200


def test_inventory_alerts_returns_200():
    with patch('src.api.routers.inventory.get_engine', return_value=make_mock_engine(rows=[])):
        response = client.get('/api/v1/inventory/alerts')
    assert response.status_code == 200


def test_pipeline_runs_returns_200():
    with patch('src.api.routers.pipeline.get_engine', return_value=make_mock_engine(rows=[])):
        response = client.get('/api/v1/pipeline/runs')
    assert response.status_code == 200


def test_pipeline_runs_respects_limit():
    with patch('src.api.routers.pipeline.get_engine', return_value=make_mock_engine(rows=[])):
        response = client.get('/api/v1/pipeline/runs?limit=5')
    assert response.status_code == 200
