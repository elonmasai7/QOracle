from backend.app import create_app


def test_register_login_and_profile_flow():
    app = create_app()
    client = app.test_client()

    register = client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Acme Treasury",
            "email": "admin@acme.com",
            "password": "S3curePass!",
            "role": "admin",
        },
    )
    assert register.status_code == 201
    payload = register.get_json()
    assert payload["organization_id"]
    assert payload["user_id"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@acme.com", "password": "S3curePass!"},
    )
    assert login.status_code == 200
    token = login.get_json()["access_token"]

    profile = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert profile.status_code == 200
    me = profile.get_json()
    assert me["organization_name"] == "Acme Treasury"
    assert me["role"] == "admin"
