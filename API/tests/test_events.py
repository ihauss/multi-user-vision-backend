import pytest
from tests.utils import create_user, create_camera


def test_create_event_ok(client):
    token = create_user(client, "owner_event")

    cam_res = create_camera(client, token)
    cam_id = cam_res.json()["camera_id"]
    api_key = cam_res.json()["api_key"]

    res = client.post(
        "/events",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "camera_id": cam_id,
            "type": "motion_detected",
            "description": "movement detected",
            "importance": 2,
            "payload": {"confidence": 0.9}
        }
    )

    assert res.status_code == 200


def test_get_events_authorized(client):
    token = create_user(client, "owner_event2")

    cam_res = create_camera(client, token)
    cam_id = cam_res.json()["camera_id"]
    api_key = cam_res.json()["api_key"]

    # create event
    client.post(
        "/events",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "camera_id": cam_id,
            "type": "motion_detected",
            "description": "movement detected",
            "importance": 1
        }
    )

    res = client.get(
        f"/cameras/{cam_id}/events",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert res.status_code == 200
    assert len(res.json()) == 1


def test_get_events_unauthorized(client):
    owner_token = create_user(client, "owner_event3")
    other_token = create_user(client, "other_event3")

    cam_res = create_camera(client, owner_token)
    cam_id = cam_res.json()["camera_id"]
    api_key = cam_res.json()["api_key"]

    # create event
    client.post(
        "/events",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "camera_id": cam_id,
            "type": "intrusion",
            "importance": 2
        }
    )

    res = client.get(
        f"/cameras/{cam_id}/events",
        headers={"Authorization": f"Bearer {other_token}"}
    )

    assert res.status_code in (401, 403)
