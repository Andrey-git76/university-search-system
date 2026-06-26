def test_health_check(api_client):
    response = api_client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "University Search System"