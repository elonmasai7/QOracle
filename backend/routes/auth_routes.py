import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..auth import auth_required, get_auth_context
from ..extensions import db
from ..models import Membership, User, Tenant
from ..services.security import hash_password, verify_password


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register")
def register():
    payload = request.get_json(force=True)
    tenant_name = (payload.get("tenant_name") or payload.get("organization_name") or "").strip()
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    role = payload.get("role", "admin")

    if not tenant_name:
        return jsonify({"error": "tenant_name_required"}), 400
    if not email:
        return jsonify({"error": "email_required"}), 400
    if len(password) < 8:
        return jsonify({"error": "password_too_short"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_already_registered"}), 409

    tenant = Tenant(name=tenant_name, plan=payload.get("plan", "starter"))
    db.session.add(tenant)
    db.session.flush()

    user = User(
        tenant_id=tenant.id,
        email=email,
        password_hash=hash_password(password),
        role=role,
    )
    db.session.add(user)
    db.session.flush()

    db.session.add(
        Membership(
            tenant_id=tenant.id,
            user_id=user.id,
            role=role,
            status="active",
            is_default=True,
        )
    )
    db.session.commit()

    return jsonify({"tenant_id": str(tenant.id), "organization_id": str(tenant.id), "user_id": str(user.id)}), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(force=True)
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    user = User.query.filter_by(email=email).first()
    membership = Membership.query.filter_by(user_id=user.id, tenant_id=user.tenant_id).first() if user else None
    if (
        not user
        or not user.is_active
        or not membership
        or membership.status != "active"
        or not verify_password(password, user.password_hash)
    ):
        return jsonify({"error": "invalid_credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={
            "tenant_id": str(user.tenant_id),
            "membership_id": str(membership.id),
            "role": membership.role,
        },
    )
    return jsonify({"access_token": token, "tenant_id": str(user.tenant_id), "organization_id": str(user.tenant_id), "role": membership.role})


@auth_bp.get("/me")
@auth_required
def me():
    ctx = get_auth_context()
    try:
        user_id = uuid.UUID(str(ctx["user_id"]))
    except (TypeError, ValueError):
        return jsonify({"error": "invalid_user_context"}), 401

    user = User.query.filter_by(id=user_id).first()
    if not user:
        return jsonify({"error": "user_not_found"}), 404
    tenant = Tenant.query.filter_by(id=user.tenant_id).first()
    membership = Membership.query.filter_by(user_id=user.id, tenant_id=user.tenant_id).first()
    return jsonify(
        {
            "user_id": str(user.id),
            "tenant_id": str(user.tenant_id),
            "organization_id": str(user.tenant_id),
            "email": user.email,
            "role": membership.role if membership else user.role,
            "tenant_name": tenant.name if tenant else None,
            "organization_name": tenant.name if tenant else None,
            "plan": tenant.plan if tenant else None,
            "membership_status": membership.status if membership else None,
        }
    )
