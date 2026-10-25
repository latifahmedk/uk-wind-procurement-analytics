import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "documentation" in data

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "upstreamElexonApi" in data

def test_metadata_endpoint():
    response = client.get("/api/metadata")
    assert response.status_code == 200
    data = response.json()
    assert data["defaultCutoff"] == "11:00"
    assert len(data["datasets"]) == 2
    assert len(data["availableCutoffs"]) >= 4

def test_analysis_summary_endpoint():
    response = client.get("/api/analysis/summary?startDate=2026-01-01&endDate=2026-01-02&decisionCutoff=11:00")
    assert response.status_code == 200
    data = response.json()
    assert "maeMw" in data
    assert "rmseMw" in data
    assert "meanBiasMw" in data
    assert "totalShortfallEnergyGwh" in data

def test_accuracy_endpoint():
    response = client.get("/api/analysis/accuracy?startDate=2026-01-01&endDate=2026-01-02&decisionCutoff=11:00")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "daily" in data
    assert "hourly" in data
    assert "distribution" in data

def test_timeseries_endpoint():
    response = client.get("/api/analysis/timeseries?startDate=2026-01-01&endDate=2026-01-02&decisionCutoff=11:00")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "startTime" in item
        assert "generationForecast" in item
        assert "generationActual" in item
        assert "forecastError" in item

def test_procurement_endpoint():
    response = client.get("/api/analysis/procurement?startDate=2026-01-01&endDate=2026-01-02&decisionCutoff=11:00")
    assert response.status_code == 200
    data = response.json()
    assert "totalShortfallEnergyMwh" in data
    assert "maxShortfallMw" in data
    assert "operationalDisclaimer" in data

def test_data_export_csv():
    response = client.get("/api/data/export?startDate=2026-01-01&endDate=2026-01-02&decisionCutoff=11:00")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    csv_text = response.text
    assert "Delivery Date" in csv_text
    assert "Forecast Generation (MW)" in csv_text
    assert "Quality Status" in csv_text
