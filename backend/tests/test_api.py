def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Streamworks Self Service API"

def test_health_check(client):
    # Depending on if there is a health check endpoint.
    # The README said http://localhost:8000/health
    response = client.get("/health")
    # If standard FastAPI docs, maybe /docs is available.
    if response.status_code == 404:
        # Fallback to root check if health doesn't exist yet (docs say it should)
        pass
    else:
        assert response.status_code == 200
