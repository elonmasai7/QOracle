from io import BytesIO

from backend.app import create_app


def _auth_token(client) -> str:
    client.post(
        "/api/v1/auth/register",
        json={
            "organization_name": "Portfolio Org",
            "email": "portfolio-admin@acme.com",
            "password": "S3curePass!",
            "role": "admin",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "portfolio-admin@acme.com", "password": "S3curePass!"},
    )
    return login.get_json()["access_token"]


def test_portfolio_upload_and_detail_flow():
    app = create_app()
    client = app.test_client()
    token = _auth_token(client)

    upload = client.post(
        "/api/v1/portfolios/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "name": "Core Portfolio",
            "file": (
                BytesIO(b"symbol,quantity,price,asset_class\nAAPL,10,190,equity\nMSFT,5,420,equity\n"),
                "portfolio.csv",
            ),
        },
        content_type="multipart/form-data",
    )
    assert upload.status_code == 201
    payload = upload.get_json()
    assert payload["asset_count"] == 2
    assert payload["market_value"] == 4000.0

    detail = client.get(
        f"/api/v1/portfolios/{payload['portfolio_id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail.status_code == 200
    portfolio = detail.get_json()
    assert portfolio["asset_count"] == 2
    assert len(portfolio["holdings"]) == 2
