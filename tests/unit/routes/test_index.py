def test_index(test_client):
    resp = test_client.get("/index", follow_redirects=True)
    assert b"Travis' Custom Fuel Logger" in resp.data

    resp = test_client.get("/", follow_redirects=True)
    assert b"Travis' Custom Fuel Logger" in resp.data