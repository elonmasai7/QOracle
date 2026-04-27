import csv
import io
import uuid
from flask import Blueprint, jsonify, request
from ..auth import auth_required, get_auth_context, role_required
from ..extensions import db
from ..models import Portfolio, Asset
from ..services.audit import write_audit_log
from ..services.platform_data import validate_portfolio_payload


portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/v1/portfolios")


@portfolio_bp.post("/upload")
@auth_required
@role_required("admin", "analyst")
def upload_portfolio():
    ctx = get_auth_context()
    tenant_id = ctx["tenant_id"]

    name = request.form.get("name", "Uploaded Portfolio")
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "file_required"}), 400

    if not f.filename.endswith(".csv"):
        return jsonify({"error": "only_csv_allowed"}), 400

    csv_data = io.StringIO(f.stream.read().decode("utf-8"))
    reader = csv.DictReader(csv_data)
    rows = list(reader)
    validation = validate_portfolio_payload(rows)
    if not validation["valid"]:
        return jsonify(validation), 422

    tenant_uuid = uuid.UUID(tenant_id)
    portfolio = Portfolio(tenant_id=tenant_uuid, name=name, source="csv")
    db.session.add(portfolio)
    db.session.flush()

    asset_count = 0
    market_value = 0.0
    for row in rows:
        quantity = float(row["quantity"])
        price = float(row["price"])
        asset = Asset(
            tenant_id=tenant_uuid,
            portfolio_id=portfolio.id,
            symbol=row["symbol"],
            quantity=quantity,
            price=price,
            asset_class=row.get("asset_class", "equity"),
        )
        db.session.add(asset)
        asset_count += 1
        market_value += quantity * price

    db.session.commit()
    write_audit_log(
        tenant_id,
        "portfolio_upload",
        "portfolio",
        {"portfolio_id": str(portfolio.id)},
        user_id=ctx.get("user_id"),
    )
    return (
        jsonify(
            {
                "portfolio_id": str(portfolio.id),
                "asset_count": asset_count,
                "market_value": round(market_value, 2),
                "validation": validation,
            }
        ),
        201,
    )


@portfolio_bp.get("/")
@auth_required
def list_portfolios():
    ctx = get_auth_context()
    tenant_id = ctx["tenant_id"]

    rows = Portfolio.query.filter_by(tenant_id=uuid.UUID(tenant_id)).all()
    return jsonify(
        [
            {
                "id": str(r.id),
                "name": r.name,
                "source": r.source,
                "asset_count": Asset.query.filter_by(portfolio_id=r.id, tenant_id=uuid.UUID(tenant_id)).count(),
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    )


@portfolio_bp.get("/<portfolio_id>")
@auth_required
def get_portfolio(portfolio_id):
    ctx = get_auth_context()
    tenant_uuid = uuid.UUID(ctx["tenant_id"])
    portfolio_uuid = uuid.UUID(portfolio_id)

    portfolio = Portfolio.query.filter_by(id=portfolio_uuid, tenant_id=tenant_uuid).first()
    if not portfolio:
        return jsonify({"error": "portfolio_not_found"}), 404

    assets = Asset.query.filter_by(portfolio_id=portfolio.id, tenant_id=tenant_uuid).all()
    holdings = [
        {
            "id": str(asset.id),
            "symbol": asset.symbol,
            "quantity": asset.quantity,
            "price": asset.price,
            "asset_class": asset.asset_class,
            "market_value": round(asset.quantity * asset.price, 2),
        }
        for asset in assets
    ]

    return jsonify(
        {
            "id": str(portfolio.id),
            "name": portfolio.name,
            "source": portfolio.source,
            "created_at": portfolio.created_at.isoformat(),
            "asset_count": len(holdings),
            "market_value": round(sum(item["market_value"] for item in holdings), 2),
            "holdings": holdings,
        }
    )


@portfolio_bp.post("/validate")
@auth_required
@role_required("admin", "analyst")
def validate_portfolio():
    payload = request.get_json(force=True)
    rows = payload.get("rows", [])
    result = validate_portfolio_payload(rows)
    return jsonify(result), (200 if result["valid"] else 422)
