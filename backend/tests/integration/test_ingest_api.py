import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["message"] == "DevLens Backend Service Healthy"


@pytest.mark.asyncio
async def test_ingest_endpoint_github(client: AsyncClient):
    payload = {
        "source": "github",
        "url": "https://github.com/vercel/next-learn",
        "branch": "main",
    }
    response = await client.post("/api/v1/ingest", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "repo_id" in data
    assert data["status"] == "queued"
