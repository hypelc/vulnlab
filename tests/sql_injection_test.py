def test_sql_injection_does_not_bypass_login(client):
    client.post (
        "/login",
        data = {"username": "' OR '1'='1' -- ", "password": "asdasdad"},
    )

    response = client.get ("/admin")

    assert response.status_code == 302