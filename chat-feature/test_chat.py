# test_chat.py
from fastapi.testclient import TestClient
from main import app
import pytest

client = TestClient(app)
def test_create_chat_room():
    # First, login to get token
    login_response = client.post("/auth/login", json={
        "username": "testuser",
        "password": "testpass"
    })
    token = login_response.json()["access_token"]

    # Create room with auth
    response = client.post(
        "/chat_rooms/",
        json={"name": "Test Chat Room", "description": "A test chat  room"},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Test Chat Room"
def test_send_message():
    # Test message sending through WebSocket
    # This would require a more complex WebSocket testing setup
    pass
