def test_non_admin_cannot_access_admin_page(client):
    client.post (
        '/login',
        data = {"username": "alice", "password": "alice123"},
    )
    response = client.get ("/admin?admin=1")

    assert response.status_code == 403

def test_non_user_cannot_access_admin_page(client):
    response = client.get ("/admin?admin=1")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]

def test_admin_can_access_adming_page(client):
    client.post (
        "/login",
        data = {"username": "admin", "password": "admin123"},
    )
    response = client.get ("/admin")

    assert response.status_code == 200


