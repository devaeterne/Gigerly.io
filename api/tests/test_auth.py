import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    payload = {"email": "newuser@example.com", "password": "strongpass123"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client, test_user):
    payload = {"email": test_user.email, "password": "password123"}
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client):
    payload = {"email": "loginuser@example.com", "password": "password123"}
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    payload = {"email": "wrongpass@example.com", "password": "correctpass"}
    await client.post("/auth/register", json=payload)
    response = await client.post(
        "/auth/login", json={"email": payload["email"], "password": "badpass"}
    )
    assert response.status_code == 401

