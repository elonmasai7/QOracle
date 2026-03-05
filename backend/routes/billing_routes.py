import uuid
from flask import Blueprint, jsonify
from ..auth import auth_required, get_auth_context
from ..models import BillingRecord


billing_bp = Blueprint("billing", __name__, url_prefix="/api/v1/billing")


@billing_bp.get("/usage")
@auth_required
def usage():
    ctx = get_auth_context()
    tenant_id = ctx["tenant_id"]
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
