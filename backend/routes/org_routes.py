import uuid
from flask import Blueprint, jsonify

from ..auth import auth_required, get_auth_context
from ..models import Membership, Tenant, User


org_bp = Blueprint("organizations", __name__, url_prefix="/api/v1/organizations")


@org_bp.get("/current")
@auth_required
def current_organization():
    ctx = get_auth_context()
    tenant = Tenant.query.filter_by(id=uuid.UUID(str(ctx["tenant_id"]))).first()
    if not tenant:
        return jsonify({"error": "organization_not_found"}), 404

    memberships = (
        Membership.query.filter_by(tenant_id=tenant.id, status="active")
        .order_by(Membership.created_at.asc())
        .all()
    )
    member_ids = [membership.user_id for membership in memberships]
    users = {
        user.id: user
        for user in User.query.filter(User.id.in_(member_ids)).all()
    } if member_ids else {}

    return jsonify(
        {
            "id": str(tenant.id),
            "name": tenant.name,
            "plan": tenant.plan,
            "memberships": [
                {
                    "id": str(membership.id),
                    "user_id": str(membership.user_id),
                    "email": users.get(membership.user_id).email if users.get(membership.user_id) else None,
                    "role": membership.role,
                    "status": membership.status,
                    "is_default": membership.is_default,
                }
                for membership in memberships
            ],
        }
    )
