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
