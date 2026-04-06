from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_user(client):
    response = client.post("/users/", json={
        "username": "testuser",
        "password": "1234"
    })

    print(response.status_code)
    print(response.json())

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_login(client):
    client.post("/users/", json={
        "username": "loginuser",
        "password": "1234"
    })

    response = client.post("/users/login", json={
        "username": "loginuser",
        "password": "1234"
    })

    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_me(client):
    res = client.post("/users/", json={
        "username": "meuser",
        "password": "1234"
    })

    token = res.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == "meuser"


def test_login_fail(client):
    response = client.post("/users/login", json={
        "username": "unknown",
        "password": "wrong"
    })

    assert response.status_code == 401


def test_delete_me(client):
    res = client.post("/users/", json={
        "username": "deleteuser",
        "password": "1234"
    })
    token = res.json()["access_token"]

    response = client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    login = client.post("/users/login", json={
        "username": "deleteuser",
        "password": "1234"
    })

    assert login.status_code == 401
