import conftest

def test_search_escapes_html_input(client):

    # Script used in tests
    payload = "<script>alert(1)</script>"

    # Simulate the payload being inserted into the query (q)
    response = client.get(
        "/search",
        query_string={"q": payload},
    )

    # Asserts to verify the HTTP status, the format of response containing the expected characters instead of the script
    assert response.status_code == 200
    assert b"&lt;script&gt;" in response.data
    assert b"<script>alert(1)</script>" not in response.data