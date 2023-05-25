def test_get_user_by_id(test_client, basic_auth_header, test_user_id, test_username):
    resp = test_client.get(f"/api/users/{test_user_id}", headers=basic_auth_header)
    assert resp.status_code == 200
    assert resp.json.get("username") == test_username


def test_list_user(test_client, basic_auth_header, test_user_id):
    resp = test_client.get("/api/users", headers=basic_auth_header)
    assert resp.status_code == 200
    assert len(resp.json) > 0
    assert test_user_id in [u.get("id") for u in resp.json]
