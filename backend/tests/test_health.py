import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data
    assert "X-Correlation-ID" in response.headers
    assert "X-Response-Time-Ms" in response.headers


@pytest.mark.asyncio
async def test_openapi_docs_accessible(client: AsyncClient):
    response = await client.get("/docs")
    assert response.status_code == 200
