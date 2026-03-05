import uuid
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from ..auth import auth_required, get_auth_context, role_required
from ..extensions import db
from ..models import ApiKey
from ..services.audit import write_audit_log
from ..services.security import generate_api_key_token, hash_api_key_token


api_key_bp = Blueprint("api_keys", __name__, url_prefix="/api/v1/api-keys")


@api_key_bp.post("")
@auth_required
@role_required("admin")
def create_api_key():
    ctx = get_auth_context()
    if ctx.get("auth_type") != "jwt":
        return jsonify({"error": "jwt_required_for_key_management"}), 403

    payload = request.get_json(force=True)
    tenant_id = uuid.UUID(ctx["tenant_id"])

    raw_key = generate_api_key_token()
    expires_days = int(payload.get("expires_days", 365))
    expires_at = datetime.utcnow() + timedelta(days=expires_days) if expires_days > 0 else None

    row = ApiKey(
        tenant_id=tenant_id,
        name=payload.get("name", "Enterprise Integration Key"),
        key_prefix=raw_key[:24],
        key_hash=hash_api_key_token(raw_key),
        role=payload.get("role", "analyst"),
        expires_at=expires_at,
    )
    db.session.add(row)
    db.session.commit()

    write_audit_log(
        tenant_id,
        "api_key_create",
        "api_key",
        {"api_key_id": str(row.id), "name": row.name, "role": row.role},
        user_id=ctx.get("user_id"),
    )

    return (
        jsonify(
            {
                "id": str(row.id),
                "name": row.name,
                "role": row.role,
                "expires_at": row.expires_at.isoformat() if row.expires_at else None,
                "api_key": raw_key,
                "note": "Store this key now. It will not be shown again.",
            }
        ),
        201,
    )


@api_key_bp.get("")
@auth_required
@role_required("admin")
def list_api_keys():
    ctx = get_auth_context()
    tenant_id = uuid.UUID(ctx["tenant_id"])

    rows = ApiKey.query.filter_by(tenant_id=tenant_id).order_by(ApiKey.created_at.desc()).all()
    return jsonify(
        [
            {
                "id": str(r.id),
                "name": r.name,
                "role": r.role,
                "key_prefix": r.key_prefix,
                "active": r.active,
                "expires_at": r.expires_at.isoformat() if r.expires_at else None,
                "last_used_at": r.last_used_at.isoformat() if r.last_used_at else None,
                "created_at": r.created_at.isoformat(),
            }
            for r in rows
        ]
    )


@api_key_bp.post("/<api_key_id>/revoke")
@auth_required
@role_required("admin")
def revoke_api_key(api_key_id):
    ctx = get_auth_context()
    tenant_id = uuid.UUID(ctx["tenant_id"])

    row = ApiKey.query.filter_by(id=uuid.UUID(api_key_id), tenant_id=tenant_id).first()
    if not row:
        return jsonify({"error": "api_key_not_found"}), 404

    row.active = False
    db.session.commit()
    write_audit_log(
        tenant_id,
        "api_key_revoke",
        "api_key",
        {"api_key_id": api_key_id},
        user_id=ctx.get("user_id"),
    )
    return jsonify({"revoked": True})
