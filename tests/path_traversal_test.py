def test_download_rejects_path_traversal(client):
    # Simulates the request from user altering the file:/download to file/../secret.txt
    #"/download" is the endpoint at the code, in line 184 in app.py 
    response = client.get(
        "/download",
        query_string={"file": "../secret.txt"},
    )

    assert response.status_code == 403
