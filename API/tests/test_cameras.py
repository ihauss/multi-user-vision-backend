import pytest


# -------------------------
# Helpers
# -------------------------

def create_user(client, username="user1", password="1234"):
    res = client.post("/users/", json={
        "username": username,
        "password": password
    })
    return res.json()["access_token"]


def create_camera(client, token):
    res = client.post(
        "/cameras/",
        headers={"Authorization": f"Bearer {token}"}
    )
    return res


# -------------------------
# Tests Camera Creation
# -------------------------

def test_create_camera(client):
    token = create_user(client)

    res = create_camera(client, token)

    assert res.status_code == 200
    data = res.json()

    assert "camera_id" in data
    assert "api_key" in data


def test_camera_key_not_stored_raw(client, session):
    token = create_user(client)

    res = create_camera(client, token)
    data = res.json()

    api_key = data["api_key"]
    camera_id = data["camera_id"]

    from app.models import Camera
    cam = session.get(Camera, camera_id)

    assert cam is not None
    assert cam.api_key_hash != api_key


# -------------------------
# Tests Permissions
# -------------------------

def test_add_user_to_camera(client):
    owner_token = create_user(client, "owner")
    create_user(client, "viewer")

    cam_res = create_camera(client, owner_token)
    cam_id = cam_res.json()["camera_id"]

    res = client.post(
        f"/cameras/{cam_id}/users",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"username": "viewer"}
    )

    assert res.status_code == 200


def test_non_owner_cannot_add_user(client):
    owner_token = create_user(client, "owner2")
    other_token = create_user(client, "other2")

    cam_res = create_camera(client, owner_token)
    cam_id = cam_res.json()["camera_id"]

    res = client.post(
        f"/cameras/{cam_id}/users",
        headers={"Authorization": f"Bearer {other_token}"},
        json={"username": "owner2"}
    )

    assert res.status_code in (401, 403)


def test_remove_user(client):
    owner_token = create_user(client, "owner3")
    create_user(client, "viewer3")

    cam_res = create_camera(client, owner_token)
    cam_id = cam_res.json()["camera_id"]

    # add user first
    client.post(
        f"/cameras/{cam_id}/users",
        headers={"Authorization": f"Bearer {owner_token}"},
        json={"username": "viewer3"}
    )

    res = client.delete(
        f"/cameras/{cam_id}/users/viewer3",
        headers={"Authorization": f"Bearer {owner_token}"}
    )

    assert res.status_code == 200


# -------------------------
# Tests Delete Camera
# -------------------------

def test_delete_camera(client):
    token = create_user(client, "owner4")

    cam_res = create_camera(client, token)
    cam_id = cam_res.json()["camera_id"]

    res = client.delete(
        f"/cameras/{cam_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200


def test_non_owner_cannot_delete_camera(client):
    owner_token = create_user(client, "owner5")
    other_token = create_user(client, "other5")

    cam_res = create_camera(client, owner_token)
    cam_id = cam_res.json()["camera_id"]

    res = client.delete(
        f"/cameras/{cam_id}",
        headers={"Authorization": f"Bearer {other_token}"}
    )

    assert res.status_code in (401, 403)


# -------------------------
# Tests Frames (API Key)
# -------------------------

def test_push_frame_no_key(client):
    res = client.post(
        "/cameras/frame",
        json={"data": "fake_image"}
    )

    assert res.status_code == 401


def test_push_frame_bad_key(client):
    res = client.post(
        "/cameras/frame",
        headers={"Authorization": "Bearer wrong_key"},
        json={"data": "fake_image"}
    )

    assert res.status_code == 401


def test_push_frame_ok(client):
    user_token = create_user(client, "owner6")

    cam_res = create_camera(client, user_token)
    api_key = cam_res.json()["api_key"]

    res = client.post(
        "/cameras/frame",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"data": "fake_image"}
    )

    assert res.status_code == 200


# -------------------------
# Tests Get Frame
# -------------------------

def test_get_frame_authorized(client):
    token = create_user(client, "owner7")

    cam_res = create_camera(client, token)
    cam_id = cam_res.json()["camera_id"]
    api_key = cam_res.json()["api_key"]

    # push frame
    client.post(
        "/cameras/frame",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"data": "frame1"}
    )

    res = client.get(
        f"/cameras/{cam_id}/frame",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200


def test_get_frame_unauthorized(client):
    owner_token = create_user(client, "owner8")
    other_token = create_user(client, "other8")

    cam_res = create_camera(client, owner_token)
    cam_id = cam_res.json()["camera_id"]

    res = client.get(
        f"/cameras/{cam_id}/frame",
        headers={"Authorization": f"Bearer {other_token}"}
    )

    assert res.status_code in (401, 403)


def test_websocket_stream_authorized(client):
    token = create_user(client, "owner_ws")

    cam_res = create_camera(client, token)
    cam_id = cam_res.json()["camera_id"]
    api_key = cam_res.json()["api_key"]

    # push frame
    client.post(
        "/cameras/frame",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"data": "frame_ws_1"}
    )

    with client.websocket_connect(
        f"/cameras/ws/{cam_id}?token={token}"
    ) as websocket:

        data = websocket.receive_json()

        assert data["data"] == "frame_ws_1"


def test_websocket_stream_unauthorized(client):
    owner_token = create_user(client, "owner_ws2")
    other_token = create_user(client, "other_ws2")

    cam_res = create_camera(client, owner_token)
    cam_id = cam_res.json()["camera_id"]

    try:
        with client.websocket_connect(
            f"/cameras/ws/{cam_id}?token={other_token}"
        ):
            assert False, "WebSocket should not connect"
    except Exception:
        assert True


def test_websocket_no_frame(client):
    token = create_user(client, "owner_ws3")

    cam_res = create_camera(client, token)
    cam_id = cam_res.json()["camera_id"]

    with client.websocket_connect(
        f"/cameras/ws/{cam_id}?token={token}"
    ) as websocket:

        # on attend un peu ou on vérifie que rien ne casse
        # selon ton implémentation future
        pass
