"""
tests/test_api.py
Basic tests for register/login/generate-content/history flows.
AI calls are mocked so no API key or network access is needed.

Run with: pytest tests/test_api.py -v
"""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import Base, get_db
from main import app

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    def override_get_db():
        try:
            yield session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    session.close()
    Base.metadata.drop_all(bind=engine)


def register_and_login(client):
    client.post(
        "/register",
        json={"name": "Jane", "email": "jane@example.com", "password": "StrongPass123"},
    )
    login = client.post(
        "/login", data={"username": "jane@example.com", "password": "StrongPass123"}
    )
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    headers = register_and_login(client)
    assert "Authorization" in headers


def test_login_wrong_password(client):
    client.post(
        "/register",
        json={"name": "Jane", "email": "jane@example.com", "password": "StrongPass123"},
    )
    response = client.post("/login", data={"username": "jane@example.com", "password": "Wrong"})
    assert response.status_code == 401


@patch("routes.content.ai_service.generate_ai_content")
def test_generate_content_and_history(mock_generate, client):
    mock_generate.return_value = (
        "Generate a product description for Wireless Earbuds with a professional tone.",
        "Experience crystal-clear sound with our Wireless Earbuds.",
    )
    headers = register_and_login(client)

    response = client.post(
        "/generate-content",
        json={
            "content_type": "product_description",
            "product_name": "Wireless Earbuds",
            "tone": "professional",
        },
        headers=headers,
    )
    assert response.status_code == 201
    content_id = response.json()["id"]
    assert "Earbuds" in response.json()["generated_content"]

    history = client.get("/history", headers=headers)
    assert history.status_code == 200
    assert history.json()["total"] == 1

    delete_resp = client.delete(f"/history/{content_id}", headers=headers)
    assert delete_resp.status_code == 204

    history_after = client.get("/history", headers=headers)
    assert history_after.json()["total"] == 0


def test_generate_content_requires_auth(client):
    response = client.post(
        "/generate-content",
        json={"content_type": "blog_article", "product_name": "Test"},
    )
    assert response.status_code == 401
