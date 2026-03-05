import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from ..extensions import db
from ..models import User, Tenant
from ..services.security import hash_password, verify_password


auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.post("/register")
def register():
    payload = request.get_json(force=True)
    tenant_name = payload.get("tenant_name")
    email = payload.get("email")
    password = payload.get("password")
    role = payload.get("role", "admin")

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
    db.session.commit()

    return jsonify({"tenant_id": str(tenant.id), "user_id": str(user.id)}), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(force=True)
    email = payload.get("email")
    password = payload.get("password")

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password_hash):
        return jsonify({"error": "invalid_credentials"}), 401

    token = create_access_token(
        identity=str(user.id),
        additional_claims={"tenant_id": str(user.tenant_id), "role": user.role},
    )
    return jsonify({"access_token": token, "tenant_id": str(user.tenant_id), "role": user.role})
