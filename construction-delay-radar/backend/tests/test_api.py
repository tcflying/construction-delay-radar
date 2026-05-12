import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_create_project(client):
    response = await client.post("/api/projects/", json={
        "name": "Test Project",
        "location": "Beijing",
        "start_date": "2026-07-01",
        "duration_days": 120,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert "id" in data


@pytest.mark.asyncio
async def test_predict_delay(client):
    response = await client.post("/api/predict/", json={
        "project_id": "proj_001",
        "progress_percent": 35,
        "weather_delays_days": 5,
        "resource_shortage_score": 0.6,
        "supply_chain_score": 0.4,
        "historical_performance": 0.78,
    })
    assert response.status_code == 200
    data = response.json()
    assert "predicted_delay_days" in data
    assert "confidence" in data
    assert "risk_level" in data
