import csv
import io
import uuid
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from ..auth import role_required
from ..extensions import db
from ..models import Portfolio, Asset
from ..services.audit import write_audit_log


portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/api/v1/portfolios")


@portfolio_bp.post("/upload")
@jwt_required()
@role_required("admin", "analyst")
def upload_portfolio():
    claims = get_jwt()
    tenant_id = claims["tenant_id"]

    name = request.form.get("name", "Uploaded Portfolio")
    f = request.files.get("file")
    if not f:
        return jsonify({"error": "file_required"}), 400

    # Minimal upload safety gate; plug in ClamAV sidecar in production.
    if not f.filename.endswith(".csv"):
        return jsonify({"error": "only_csv_allowed"}), 400

    portfolio = Portfolio(tenant_id=uuid.UUID(tenant_id), name=name, source="csv")
    db.session.add(portfolio)
    db.session.flush()

    csv_data = io.StringIO(f.stream.read().decode("utf-8"))
    reader = csv.DictReader(csv_data)
    for row in reader:
        asset = Asset(
            tenant_id=uuid.UUID(tenant_id),
            portfolio_id=portfolio.id,
            symbol=row["symbol"],
            quantity=float(row["quantity"]),
            price=float(row["price"]),
            asset_class=row.get("asset_class", "equity"),
        )
        db.session.add(asset)

    db.session.commit()
    write_audit_log(tenant_id, "portfolio_upload", "portfolio", {"portfolio_id": str(portfolio.id)})
    return jsonify({"portfolio_id": str(portfolio.id)}), 201


@portfolio_bp.get("/")
@jwt_required()
def list_portfolios():
    claims = get_jwt()
    tenant_id = claims["tenant_id"]

    rows = Portfolio.query.filter_by(tenant_id=uuid.UUID(tenant_id)).all()
    return jsonify(
        [
            {
                "id": str(r.id),
                "name": r.name,
                "source": r.source,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    )
