from backend.app import create_app


def test_dashboard_overview_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/v1/dashboard/overview")

    assert response.status_code == 200
    payload = response.get_json()
    assert "metrics" in payload
    assert "reports" in payload
