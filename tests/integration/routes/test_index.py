def test_index(test_client):
    resp = test_client.get("/index", follow_redirects=True)
    assert "Fuel Logger App" in resp.text

    resp = test_client.get("/", follow_redirects=True)
    assert "Fuel Logger App" in resp.text
