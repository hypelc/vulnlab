# IDOR Test config
def test_user_can_access_own_note(client):

    # Simulate the Alice's login into the system
    client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
    )

    # Simulate the Alice's request to notes/1
    response = client.get("/notes/1")

    # Verify if after the request the http code is 200 OK, and in assert b, if the program show the string after accessing it
    # this is the expected
    assert response.status_code == 200
    assert b"Alice private note" in response.data

def test_user_cannot_access_another_note(client):

    # Simulate the Alice's login into the system
    client.post(
        "/login",
        data={"username": "alice", "password": "alice123"},
    )

    # Simulate the Alice's request to notes/2
    response = client.get("/notes/2")

    # Verify if after the request the http code is 404. this is the expected
    assert response.status_code == 404

def test_anauthorized_user_redirect(client):
    response = client.get("/notes/2")

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]