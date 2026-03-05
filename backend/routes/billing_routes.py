import uuid
from flask import Blueprint, jsonify
from flask_jwt_extended import get_jwt, jwt_required
from ..models import BillingRecord


billing_bp = Blueprint("billing", __name__, url_prefix="/api/v1/billing")


@billing_bp.get("/usage")
@jwt_required()
def usage():
    claims = get_jwt()
    tenant_id = claims["tenant_id"]
    rows = BillingRecord.query.filter_by(tenant_id=uuid.UUID(tenant_id)).all()
    return jsonify(
        [
            {
                "usage_type": r.usage_type,
                "units": r.units,
                "unit_price": r.unit_price,
                "total": r.total,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    )
