def test_read_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json() == {
        "service": "Read Model Updater",
        "version": "1.0.0",
        "description": "Maintains materialized views and provides read endpoints",
    }


def test_docs_available(client):
    resp = client.get("/docs")
    assert resp.status_code == 200


def test_openapi_metadata(client):
    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    data = resp.json()
    assert data["info"]["title"] == "Read Model Updater Service"
