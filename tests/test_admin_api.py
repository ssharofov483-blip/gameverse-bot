import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.config import settings
from app.core.database import get_db


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["game"] == "GAMEVERSE"


@pytest.mark.asyncio
async def test_admin_overview_auth(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            # Without auth header
            res_unauth = await ac.get("/api/admin/overview")
            assert res_unauth.status_code == 401

            # With correct auth header
            headers = {"X-Admin-API-Key": settings.ADMIN_API_KEY}
            res_auth = await ac.get("/api/admin/overview", headers=headers)
            assert res_auth.status_code == 200
            data = res_auth.json()
            assert "total_users" in data
            assert "total_kingdoms" in data
            assert "total_battles" in data
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_admin_players_listing(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db
    try:
        headers = {"X-Admin-API-Key": settings.ADMIN_API_KEY}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            res = await ac.get("/api/admin/players?limit=10", headers=headers)
            assert res.status_code == 200
            assert isinstance(res.json(), list)
    finally:
        app.dependency_overrides.clear()
